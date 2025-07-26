import os
import random
import shutil
from tkinter import messagebox
from PIL import Image, ImageTk

class ImageSorter:
    def __init__(self, parent_window, img_label, folder_path, tiers, on_close_callback):
        self.parent_window = parent_window
        self.img_label = img_label
        self.folder_path = folder_path
        self.tiers = tiers
        self.on_close_callback = on_close_callback

        self.image_files = []
        self.current_image = None
        self.selected_tier = None
        
        self.parent_window.protocol("WM_DELETE_WINDOW", self.on_window_close)

    def start(self):
        self.image_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp"))]
        random.shuffle(self.image_files)
        self.next_image()

    def on_tier_select(self, tier):
        self.selected_tier = tier
        if self.selected_tier:
            self.move_file()
        self.next_image()

    def move_file(self):
        if self.selected_tier and self.current_image:
            src = os.path.join(self.folder_path, self.current_image)
            dst = os.path.join(self.folder_path, self.selected_tier, self.current_image)
            try:
                shutil.move(src, dst)
            except Exception as e:
                messagebox.showerror("File Error", f"Could not move file: {self.current_image}\nError: {e}")

    def next_image(self):
        if not self.image_files:
            messagebox.showinfo("Done", "All images have been sorted!")
            self.on_window_close()
            return

        self.current_image = self.image_files.pop()
        image_path = os.path.join(self.folder_path, self.current_image)

        try:
            with Image.open(image_path) as img:
                img.thumbnail((854, 480))
                img_tk = ImageTk.PhotoImage(img)
                self.img_label.config(image=img_tk)
                self.img_label.image = img_tk
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {self.current_image}\n{e}")
            self.next_image() # Skip to the next one

    def on_window_close(self):
        self.parent_window.destroy()
        self.on_close_callback()