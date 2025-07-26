import os
import cv2
import random
import shutil
import threading
import queue
import time
from tkinter import messagebox
from PIL import Image, ImageTk

class VideoSorter:
    def __init__(self, parent_window, img_label, folder_path, tiers, on_close_callback):
        self.parent_window = parent_window
        self.img_label = img_label
        self.folder_path = folder_path
        self.tiers = tiers
        self.on_close_callback = on_close_callback

        self.video_files = []
        self.current_video = None # Stores the filename of the video currently on display

        # --- Threading Safety ---
        self.video_cap = None
        self.stop_playback = threading.Event()
        self.video_lock = threading.Lock()
        self.frame_queue = queue.Queue(maxsize=30)
        
        self.parent_window.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def start(self):
        """Loads video files and starts the sorter by calling next_video."""
        all_files = os.listdir(self.folder_path)
        self.video_files = [f for f in all_files if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm"))]
        
        # Filter out files that might be in tier subdirectories already
        self.video_files = [f for f in self.video_files if os.path.isfile(os.path.join(self.folder_path, f))]
        
        random.shuffle(self.video_files)
        
        if not self.video_files:
            messagebox.showinfo("No Videos Found", "There are no videos in the root of the selected folder to sort.")
            self.on_window_close()
            return

        self.parent_window.after(100, self.next_video)
        self.display_frame_from_queue()

    def on_tier_select(self, tier):
        """Signals the stop and triggers the transition to the next video."""
        if not self.stop_playback.is_set():
            self.stop_playback.set()
            # Pass the selected tier to next_video, which will handle the file move
            self.next_video(tier_for_previous=tier)

    def move_file(self, video_to_move, tier):
        """Moves the specified video file to its new tier folder."""
        src = os.path.join(self.folder_path, video_to_move)
        dst = os.path.join(self.folder_path, tier, video_to_move)
        try:
            print(f"Moving {src} to {dst}")
            shutil.move(src, dst)
        except Exception as e:
            messagebox.showerror("File Move Error", f"Could not move file: {video_to_move}\n\nError: {e}")

    def next_video(self, tier_for_previous=None):
        """
        Manages the transition: releases the old video, moves the file, and loads the new video.
        This is the core of the fix.
        """
        # --- 1. Cleanup and File Move ---
        with self.video_lock:
            if self.video_cap:
                self.video_cap.release() # This releases the file handle.
            self.video_cap = None
        
        # Now that the file is released, move the *previous* video if a tier was selected.
        if tier_for_previous and self.current_video:
            self.move_file(self.current_video, tier_for_previous)

        # --- 2. Load Next Video ---
        if not self.video_files:
            messagebox.showinfo("Done", "All videos have been sorted!")
            self.on_window_close()
            return

        self.current_video = self.video_files.pop()
        video_path = os.path.join(self.folder_path, self.current_video)
        
        self.stop_playback.clear() # Reset the event for the new video
        new_cap = cv2.VideoCapture(video_path)

        with self.video_lock:
            if new_cap.isOpened():
                self.video_cap = new_cap
                threading.Thread(target=self.video_playback_thread, daemon=True).start()
            else:
                messagebox.showerror("Error", f"Could not open video: {self.current_video}. Skipping file.")
                self.parent_window.after(50, self.next_video)

    def video_playback_thread(self):
        """Reads frames from the video in a background thread."""
        while not self.stop_playback.is_set():
            frame = None
            read_success = False
            with self.video_lock:
                if self.video_cap and self.video_cap.isOpened():
                    try:
                        read_success, frame = self.video_cap.read()
                    except cv2.error:
                        self.stop_playback.set() # Stop on error
                        break
            
            if not read_success:
                with self.video_lock:
                    if self.video_cap:
                        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                try:
                    self.frame_queue.put_nowait(frame_rgb)
                except queue.Full:
                    pass
            time.sleep(0.02)

    def display_frame_from_queue(self):
        """Gets frames from the queue and displays them."""
        try:
            frame = self.frame_queue.get_nowait()
            img = Image.fromarray(frame)
            img.thumbnail((854, 480))
            img_tk = ImageTk.PhotoImage(image=img)
            
            if self.img_label.winfo_exists():
                self.img_label.config(image=img_tk)
                self.img_label.image = img_tk
        except queue.Empty:
            pass
        finally:
            if self.parent_window.winfo_exists():
                self.parent_window.after(15, self.display_frame_from_queue)

    def on_window_close(self):
        """Stops video, cleans up resources, and calls the main window callback."""
        self.stop_playback.set()
        with self.video_lock:
            if self.video_cap:
                self.video_cap.release()
                self.video_cap = None
        self.parent_window.destroy()
        self.on_close_callback()