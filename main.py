import os
import cv2
import random
import shutil
import threading
import queue
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

class MediaSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Tier Sorter")
        self.root.geometry("400x250")

        # --- UI Elements ---
        # Mode Selection
        self.mode_var = tk.StringVar(value="Pictures")
        tk.Label(root, text="Select Mode:").pack(pady=5)
        tk.Radiobutton(root, text="Pictures", variable=self.mode_var, value="Pictures").pack()
        tk.Radiobutton(root, text="Videos", variable=self.mode_var, value="Videos").pack()

        # Folder Path
        self.folder_path_var = tk.StringVar()
        tk.Label(root, text="Select Folder:").pack(pady=5)
        tk.Button(root, text="Browse", command=self.browse_folder).pack()
        self.folder_label = tk.Label(root, text="No folder selected")
        self.folder_label.pack()

        # Tiers
        self.tiers_var = tk.StringVar(value="S, A, B, C, Skip")
        tk.Label(root, text="Tiers (comma-separated):").pack(pady=5)
        tk.Entry(root, textvariable=self.tiers_var, width=50).pack()

        # Start Button
        tk.Button(root, text="Start Sorting", command=self.start_sorting, bg="green", fg="white").pack(pady=20)

        # --- Sorter specific variables ---
        self.sorter_window = None
        self.img_label = None
        self.video_files = []
        self.image_files = []
        self.current_media = None
        self.video_cap = None
        self.stop_video = False
        self.frame_queue = queue.Queue()
        self.selected_tier = None

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path_var.set(path)
            self.folder_label.config(text=path)

    def start_sorting(self):
        folder_path = self.folder_path_var.get()
        tiers = [tier.strip() for tier in self.tiers_var.get().split(',') if tier.strip()]

        if not folder_path:
            messagebox.showerror("Error", "Please select a folder.")
            return
        if not tiers:
            messagebox.showerror("Error", "Please define at least one tier.")
            return

        # Create tier subdirectories if they don't exist
        for tier in tiers:
            os.makedirs(os.path.join(folder_path, tier), exist_ok=True)

        self.root.withdraw()  # Hide the main window
        self.setup_sorter_ui(tiers)

        if self.mode_var.get() == "Videos":
            self.run_vid_sorter(folder_path, tiers)
        else:
            self.run_pic_sorter(folder_path, tiers)

    def setup_sorter_ui(self, tiers):
        self.sorter_window = tk.Toplevel(self.root)
        self.sorter_window.title(f"{self.mode_var.get()} Sorter")
        self.sorter_window.protocol("WM_DELETE_WINDOW", self.on_sorter_close)

        self.img_label = tk.Label(self.sorter_window)
        self.img_label.pack()

        button_frame = tk.Frame(self.sorter_window)
        button_frame.pack()

        for tier in tiers:
            btn = tk.Button(
                button_frame,
                text=tier,
                command=lambda t=tier: self.on_tier_select(t),
                width=10,
                height=2,
                font=("Arial", 14),
            )
            btn.pack(side=tk.LEFT, padx=10, pady=10)

    def on_sorter_close(self):
        if self.video_cap and self.video_cap.isOpened():
            self.stop_video = True
            self.video_cap.release()
        self.sorter_window.destroy()
        self.root.deiconify() # Show the main window again

    # --- Picture Sorter Logic ---
    def run_pic_sorter(self, folder_path, tiers):
        self.image_files = [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        random.shuffle(self.image_files)
        self.folder_path = folder_path
        self.next_image()

    def next_image(self):
        if not self.image_files:
            messagebox.showinfo("Done", "All images have been sorted!")
            self.on_sorter_close()
            return

        self.current_media = self.image_files.pop()
        image_path = os.path.join(self.folder_path, self.current_media)

        try:
            img = Image.open(image_path)
            img.thumbnail((854, 480))
            img_tk = ImageTk.PhotoImage(img)
            self.img_label.config(image=img_tk)
            self.img_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {self.current_media}\n{e}")
            self.next_image()

    def on_tier_select(self, tier):
        self.selected_tier = tier
        if self.mode_var.get() == "Pictures":
            self.process_image_completion()
        else:
            self.stop_video = True

    def process_image_completion(self):
        if self.selected_tier is not None and self.current_media:
            src = os.path.join(self.folder_path, self.current_media)
            dst = os.path.join(self.folder_path, self.selected_tier, self.current_media)
            shutil.move(src, dst)
            self.selected_tier = None
        self.next_image()

    # --- Video Sorter Logic ---
    def run_vid_sorter(self, folder_path, tiers):
        self.video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]
        random.shuffle(self.video_files)
        self.folder_path = folder_path
        self.next_video()
        self.display_frame_from_queue()

    def next_video(self):
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None

        if not self.video_files:
            messagebox.showinfo("Done", "All videos have been sorted!")
            self.on_sorter_close()
            return

        self.current_media = self.video_files.pop()
        video_path = os.path.join(self.folder_path, self.current_media)
        self.video_cap = cv2.VideoCapture(video_path)

        if self.video_cap.isOpened():
            self.stop_video = False
            threading.Thread(target=self.update_video_frame, daemon=True).start()
        else:
            messagebox.showerror("Error", f"Could not open video: {self.current_media}")
            self.next_video()
            
    def update_video_frame(self):
        while not self.stop_video and self.video_cap is not None:
            ret, frame = self.video_cap.read()
            if not ret:
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video
                continue

            frame = self.resize_frame(frame, 854, 480)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img_tk = ImageTk.PhotoImage(image=img)
            self.frame_queue.put(img_tk)
            # A small delay to control frame rate
            self.sorter_window.after(30)
        self.sorter_window.after(0, self.process_video_completion)

    def display_frame_from_queue(self):
        try:
            img_tk = self.frame_queue.get_nowait()
            if self.img_label.winfo_exists():
                self.img_label.config(image=img_tk)
                self.img_label.image = img_tk
        except queue.Empty:
            pass
        finally:
             if self.sorter_window.winfo_exists():
                self.sorter_window.after(10, self.display_frame_from_queue)

    def process_video_completion(self):
        if self.stop_video:
            if self.video_cap is not None:
                self.video_cap.release()
                self.video_cap = None
            if self.selected_tier is not None:
                src = os.path.join(self.folder_path, self.current_media)
                dst = os.path.join(self.folder_path, self.selected_tier, self.current_media)
                shutil.move(src, dst)
                self.selected_tier = None
            self.next_video()

    def resize_frame(self, frame, max_width, max_height):
        height, width = frame.shape[:2]
        if width > max_width or height > max_height:
            aspect_ratio = width / height
            if aspect_ratio > (max_width/max_height):
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            else:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            return cv2.resize(frame, (new_width, new_height))
        return frame


if __name__ == "__main__":
    root = tk.Tk()
    app = MediaSorterApp(root)
    root.mainloop()