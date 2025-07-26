import os
import tkinter as tk
from tkinter import messagebox, filedialog

# Import the logic classes from the other files
from vid_sort import VideoSorter
from img_sort import ImageSorter

class MediaSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Sorter - Setup")
        self.root.geometry("450x270")

        # --- UI Elements ---
        tk.Label(root, text="Media Sorting Tool", font=("Arial", 16)).pack(pady=(10, 20))

        # Mode Selection
        self.mode_var = tk.StringVar(value="Pictures")
        tk.Label(root, text="1. Select Mode:").pack()
        tk.Radiobutton(root, text="Pictures", variable=self.mode_var, value="Pictures").pack()
        tk.Radiobutton(root, text="Videos", variable=self.mode_var, value="Videos").pack()

        # Folder Path
        tk.Label(root, text="2. Select Folder:").pack(pady=(10, 0))
        self.folder_path_var = tk.StringVar()
        folder_frame = tk.Frame(root)
        folder_frame.pack(fill=tk.X, padx=20)
        self.folder_label = tk.Label(folder_frame, text="No folder selected", bg="white", relief="sunken", anchor="w")
        self.folder_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        tk.Button(folder_frame, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)

        # Tiers
        self.tiers_var = tk.StringVar(value="Good,Bad")
        tk.Label(root, text="3. Define Tiers (comma-separated):").pack(pady=(10,0))
        tk.Entry(root, textvariable=self.tiers_var, width=60).pack(padx=20)

        # Start Button
        tk.Button(root, text="Start Sorting", command=self.start_sorting, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=20)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.folder_path_var.set(path)
            display_path = path if len(path) < 45 else f"...{path[-42:]}"
            self.folder_label.config(text=display_path)

    def start_sorting(self):
        folder_path = self.folder_path_var.get()
        tiers = [tier.strip() for tier in self.tiers_var.get().split(',') if tier.strip()]

        # --- Input Validation ---
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Please select a valid folder.")
            return
        if not tiers:
            messagebox.showerror("Error", "Please define at least one tier.")
            return

        # --- Create Tier Folders ---
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

        # Instantiate the correct sorter logic class
        if mode == "Videos":
            sorter_logic = VideoSorter(sorter_window, img_label, folder_path, tiers, self.on_sorter_finished)
        else: # Pictures
            sorter_logic = ImageSorter(sorter_window, img_label, folder_path, tiers, self.on_sorter_finished)

        # Create tier buttons and link them to the logic's 'on_tier_select' method
        for tier in tiers:
            btn = tk.Button(
                button_frame, text=tier,
                command=lambda t=tier, s=sorter_logic: s.on_tier_select(t),
                width=10, height=2, font=("Arial", 14)
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Start the sorting process in the logic class
        sorter_logic.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaSorterApp(root)
    root.mainloop()