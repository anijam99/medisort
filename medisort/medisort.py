import os
import tkinter as tk
from tkinter import messagebox, filedialog, font

# Import the logic classes from the other files
from vid_sort import VideoSorter
from img_sort import ImageSorter

class MediaSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Sorter - Setup")
        # 1. Increased window height to ensure all elements are visible
        self.root.geometry("450x340")
        self.root.resizable(False, False) # Optional: disable resizing

        # Define styles for our custom buttons
        self.selected_bg = "#28a745"  # Green
        self.default_bg = "#e0e0e0"   # Light grey
        self.selected_fg = "white"
        self.default_fg = "black"

        # --- UI Elements ---
        tk.Label(root, text="Media Sorting Tool", font=("Arial", 18, "bold")).pack(pady=(10, 15))

        # --- Custom Mode Selection Buttons ---
        tk.Label(root, text="1. Select Mode:", font=("Arial", 10)).pack()
        self.mode_var = tk.StringVar(value="Images")
        
        mode_frame = tk.Frame(root)
        mode_frame.pack(pady=10)

        # Create labels styled as buttons
        bold_font = font.Font(family="Arial", size=11, weight="bold")
        self.pic_button = tk.Label(mode_frame, text="Images", font=bold_font, relief="raised", borderwidth=2, padx=25, pady=8)
        self.pic_button.pack(side=tk.LEFT, padx=10)
        self.pic_button.bind("<Button-1>", lambda e: self.select_mode("Images"))

        self.vid_button = tk.Label(mode_frame, text="Videos", font=bold_font, relief="raised", borderwidth=2, padx=25, pady=8)
        self.vid_button.pack(side=tk.LEFT, padx=10)
        self.vid_button.bind("<Button-1>", lambda e: self.select_mode("Videos"))

        # Set the initial state for the buttons
        self.select_mode(self.mode_var.get())

        # --- Folder Path ---
        tk.Label(root, text="2. Select Folder:", font=("Arial", 10)).pack(pady=(15, 5))
        self.folder_path_var = tk.StringVar()
        folder_frame = tk.Frame(root)
        folder_frame.pack(fill=tk.X, padx=25)
        self.folder_label = tk.Label(folder_frame, text="No folder selected", bg="white", relief="sunken", anchor="w", padx=5)
        self.folder_label.pack(side=tk.LEFT, expand=True, fill=tk.X, ipady=4, padx=(0, 5))
        tk.Button(folder_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)

        # --- Tiers ---
        self.tiers_var = tk.StringVar(value="Good, Bad, Skip")
        tk.Label(root, text="3. Define Tiers (comma-separated):", font=("Arial", 10)).pack(pady=(15, 5))
        tk.Entry(root, textvariable=self.tiers_var, width=60, font=("Arial", 10)).pack(padx=25)

        # --- Start Button ---
        start_font = font.Font(family="Arial", size=12, weight="bold")
        tk.Button(root, text="Start Sorting", command=self.start_sorting, bg="#007bff", fg="white", font=start_font, relief="flat", padx=20, pady=10).pack(pady=25)

    def select_mode(self, mode):
        """Handles the logic for clicking the custom mode buttons."""
        self.mode_var.set(mode)
        if mode == "Images":
            self.pic_button.config(background=self.selected_bg, foreground=self.selected_fg, relief="sunken")
            self.vid_button.config(background=self.default_bg, foreground=self.default_fg, relief="raised")
        else:  # Videos
            self.vid_button.config(background=self.selected_bg, foreground=self.selected_fg, relief="sunken")
            self.pic_button.config(background=self.default_bg, foreground=self.default_fg, relief="raised")

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path_var.set(path)
            display_path = path if len(path) < 45 else f"...{path[-42:]}"
            self.folder_label.config(text=display_path)

    def start_sorting(self):
        folder_path = self.folder_path_var.get()
        tiers = [tier.strip() for tier in self.tiers_var.get().split(',') if tier.strip()]

        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Please select a valid folder.")
            return
        if not tiers:
            messagebox.showerror("Error", "Please define at least one tier.")
            return

        try:
            for tier in tiers:
                os.makedirs(os.path.join(folder_path, tier), exist_ok=True)
        except Exception as e:
            messagebox.showerror("Folder Creation Error", f"Could not create tier subfolders.\nError: {e}")
            return

        self.root.withdraw()
        self.launch_sorter_window(folder_path, tiers)

    def on_sorter_finished(self):
        """Callback function to show the main window again."""
        self.root.deiconify()

    def launch_sorter_window(self, folder_path, tiers):
        sorter_window = tk.Toplevel(self.root)
        sorter_window.title(f"{self.mode_var.get()} Sorter")

        img_label = tk.Label(sorter_window)
        img_label.pack(padx=10, pady=10)

        button_frame = tk.Frame(sorter_window)
        button_frame.pack(padx=10, pady=10)

        mode = self.mode_var.get()
        sorter_logic = None

        if mode == "Videos":
            sorter_logic = VideoSorter(sorter_window, img_label, folder_path, tiers, self.on_sorter_finished)
        else:
            sorter_logic = ImageSorter(sorter_window, img_label, folder_path, tiers, self.on_sorter_finished)

        for tier in tiers:
            btn = tk.Button(
                button_frame, text=tier,
                command=lambda t=tier, s=sorter_logic: s.on_tier_select(t),
                width=10, height=2, font=("Arial", 14)
            )
            btn.pack(side=tk.LEFT, padx=5)

        sorter_logic.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaSorterApp(root)
    root.mainloop()