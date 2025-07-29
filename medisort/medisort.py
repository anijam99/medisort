import os
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from medisort.vid_sort import VideoSorter
from medisort.img_sort import ImageSorter

class MediaSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Sorter")
        self.root.geometry("500x700")
        self.root.resizable(True, True)
        
        self.root.configure(bg='#f8f9fa')
        self.primary_color = "#007bff"
        self.success_color = "#28a745"
        self.secondary_color = "#6c757d"
        self.light_bg = "#f8f9fa"
        self.card_bg = "#ffffff"
        self.border_color = "#dee2e6"

        self.mode_var = tk.StringVar(value="Images")
        self.folder_path_var = tk.StringVar()
        self.tiers_var = tk.StringVar(value="Good, Bad, Skip")

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        
        style.configure("Primary.TButton",
                       background=self.primary_color,
                       foreground="white",
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0,
                       focuscolor="none")
        
        style.configure("Success.TButton",
                       background=self.success_color,
                       foreground="white",
                       font=("Segoe UI", 12, "bold"),
                       borderwidth=0,
                       focuscolor="none")
        
        style.configure("Modern.TEntry",
                       borderwidth=1,
                       relief="solid",
                       bordercolor=self.border_color,
                       lightcolor=self.border_color,
                       darkcolor=self.border_color,
                       font=("Segoe UI", 10))

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.light_bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header_frame = tk.Frame(main_frame, bg=self.light_bg)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        
        title_label = tk.Label(header_frame, 
                              text="📁 Media Sorting Tool", 
                              font=("Segoe UI", 20, "bold"),
                              fg="#2c3e50",
                              bg=self.light_bg)
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Organize your images and videos efficiently",
                                 font=("Segoe UI", 10),
                                 fg=self.secondary_color,
                                 bg=self.light_bg)
        subtitle_label.pack(pady=(5, 0))

        card_frame = tk.Frame(main_frame, bg=self.card_bg, relief="solid", borderwidth=1)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_mode_section(card_frame)
        self.create_folder_section(card_frame)
        self.create_tiers_section(card_frame)
        self.create_start_section(card_frame)
        
        self.select_mode(self.mode_var.get())

    def create_mode_section(self, parent):
        mode_section = tk.Frame(parent, bg=self.card_bg)
        mode_section.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        tk.Label(mode_section, 
                text="Select Media Type", 
                font=("Segoe UI", 11, "bold"),
                fg="#2c3e50",
                bg=self.card_bg).pack(anchor="w")
        
        mode_buttons_frame = tk.Frame(mode_section, bg=self.card_bg)
        mode_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        self.pic_button = tk.Button(
            mode_buttons_frame,
            text="🖼️ Images",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=2,
            padx=30,
            pady=10,
            command=lambda: self.select_mode("Images")
        )
        self.pic_button.pack(side=tk.LEFT, padx=(0, 10))

        self.vid_button = tk.Button(
            mode_buttons_frame,
            text="🎥 Videos",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            borderwidth=2,
            padx=38,
            pady=10,
            command=lambda: self.select_mode("Videos")
        )
        self.vid_button.pack(side=tk.LEFT)

    def create_folder_section(self, parent):
        folder_section = tk.Frame(parent, bg=self.card_bg)
        folder_section.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(folder_section,
                text="Choose Source Folder",
                font=("Segoe UI", 11, "bold"),
                fg="#2c3e50",
                bg=self.card_bg).pack(anchor="w")
        
        folder_frame = tk.Frame(folder_section, bg=self.card_bg)
        folder_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.folder_label = tk.Label(
            folder_frame,
            text="📂 No folder selected - Click Browse to choose",
            bg="white",
            fg=self.secondary_color,
            relief="solid",
            borderwidth=1,
            anchor="w",
            padx=12,
            pady=8,
            font=("Segoe UI", 9)
        )
        self.folder_label.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        browse_btn = ttk.Button(
            folder_frame,
            text="Browse...",
            command=self.browse_folder,
        )
        browse_btn.pack(side=tk.LEFT)

    def create_tiers_section(self, parent):
        tiers_section = tk.Frame(parent, bg=self.card_bg)
        tiers_section.pack(fill=tk.X, padx=20, pady=15)

        tk.Label(tiers_section,
                text="Define Your Categories",
                font=("Segoe UI", 11, "bold"),
                fg="#2c3e50",
                bg=self.card_bg).pack(anchor="w")

        helper_label = tk.Label(tiers_section,
                text="These categories will become sorting buttons. Example: Good, Bad, Skip",
                font=("Segoe UI", 9),
                fg=self.secondary_color,
                bg=self.card_bg,
                wraplength=400,
                justify="left")
        helper_label.pack(anchor="w", pady=(5, 10))

        # Frame for input
        input_frame = tk.Frame(tiers_section, bg=self.card_bg)
        input_frame.pack(fill=tk.X)

        self.new_category_var = tk.StringVar()
        category_entry = ttk.Entry(
            input_frame,
            textvariable=self.new_category_var,
            font=("Segoe UI", 10),
            style="Modern.TEntry"
        )
        category_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        add_btn = ttk.Button(
            input_frame,
            text="Add",
            command=self.add_category
        )
        add_btn.pack(side=tk.LEFT)

        # Frame for chips
        self.chips_frame = tk.Frame(tiers_section, bg=self.card_bg)
        self.chips_frame.pack(fill=tk.X, pady=(10, 0))

        # Initialize category list
        self.categories = ["Good", "Bad", "Skip"]
        self.refresh_chips()


    def create_start_section(self, parent):
        start_section = tk.Frame(parent, bg=self.card_bg)
        start_section.pack(fill=tk.X, padx=20, pady=(20, 25))
        
        self.status_label = tk.Label(
            start_section,
            text="Ready to start sorting",
            font=("Segoe UI", 9),
            fg=self.secondary_color,
            bg=self.card_bg
        )
        self.status_label.pack(pady=(0, 10))
        
        start_btn = tk.Button(
            start_section,
            text="🚀 Start Sorting",
            command=self.start_sorting,
            bg=self.success_color,
            fg="white",
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        start_btn.pack(pady=5)

    def select_mode(self, mode):
        self.mode_var.set(mode)
        
        if mode == "Images":
            self.pic_button.config(
                bg=self.success_color,
                fg="white",
                relief="solid",
                borderwidth=2
            )
            self.vid_button.config(
                bg="#e9ecef",
                fg="#6c757d",
                relief="solid",
                borderwidth=1
            )
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Ready to sort images")
        else:
            self.vid_button.config(
                bg=self.success_color,
                fg="white",
                relief="solid",
                borderwidth=2
            )
            self.pic_button.config(
                bg="#e9ecef",
                fg="#6c757d",
                relief="solid",
                borderwidth=1
            )
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Ready to sort videos")

    def browse_folder(self):
        path = filedialog.askdirectory(title="Select folder containing your media files")
        if path:
            self.folder_path_var.set(path)
            display_path = f"📁 {os.path.basename(path)}" if len(path) < 50 else f"📁 ...{path[-45:]}"
            self.folder_label.config(text=display_path, fg="#2c3e50")
            self.status_label.config(text=f"Folder selected: {os.path.basename(path)}")

    def start_sorting(self):
        folder_path = self.folder_path_var.get()
        tiers = self.categories

        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("Invalid Folder", 
                               "Please select a valid folder containing your media files.")
            return
        
        if not tiers:
            messagebox.showerror("No Categories", 
                               "Please define at least one category for sorting.")
            return

        if len(tiers) > 8:
            if not messagebox.askyesno("Many Categories", 
                                      f"You have {len(tiers)} categories. This might make the interface crowded. Continue?"):
                return

        try:
            for tier in tiers:
                os.makedirs(os.path.join(folder_path, tier), exist_ok=True)
        except Exception as e:
            messagebox.showerror("Folder Creation Error", 
                               f"Could not create category folders.\nError: {e}")
            return

        self.status_label.config(text="Starting sorter...")
        self.root.withdraw()
        self.launch_sorter_window(folder_path, tiers)

    def on_sorter_finished(self):
        self.status_label.config(text="Sorting completed!")
        self.root.deiconify()
        messagebox.showinfo("Sorting Complete", "All media files have been processed!")

    def launch_sorter_window(self, folder_path, tiers):
        sorter_window = tk.Toplevel(self.root)
        sorter_window.title(f"{self.mode_var.get()} Sorter")
        sorter_window.configure(bg=self.light_bg)

        img_label = tk.Label(sorter_window, bg=self.light_bg)
        img_label.pack(padx=15, pady=15)

        button_frame = tk.Frame(sorter_window, bg=self.light_bg)
        button_frame.pack(padx=15, pady=(0, 15))

        mode = self.mode_var.get()
        sorter_logic = None

        if mode == "Videos":
            sorter_logic = VideoSorter(sorter_window, img_label, folder_path, tiers, self.on_sorter_finished)
        else:
            sorter_logic = ImageSorter(sorter_window, img_label, folder_path, tiers, self.on_sorter_finished)

        for i, tier in enumerate(tiers):
            btn = tk.Button(
                button_frame,
                text=tier,
                command=lambda t=tier, s=sorter_logic: s.on_tier_select(t),
                width=12,
                height=2,
                font=("Segoe UI", 12, "bold"),
                bg=self.primary_color,
                fg="white",
                relief="flat",
                borderwidth=0,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=8)
            
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.success_color))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.primary_color))

        sorter_logic.start()

    def add_category(self):
        new_cat = self.new_category_var.get().strip()
        if new_cat and new_cat not in self.categories:
            if len(self.categories) >= 8:
                messagebox.showwarning("Limit Reached", "You can only have up to 8 categories.")
                return
            self.categories.append(new_cat)
            self.new_category_var.set("")
            self.refresh_chips()
        elif new_cat in self.categories:
            messagebox.showinfo("Duplicate", "This category already exists.")

    def remove_category(self, category):
        self.categories.remove(category)
        self.refresh_chips()

    def refresh_chips(self):
        for widget in self.chips_frame.winfo_children():
            widget.destroy()

        for cat in self.categories:
            chip = tk.Frame(self.chips_frame, bg="#e9ecef", padx=8, pady=4)
            chip.pack(side=tk.LEFT, padx=5, pady=5)

            lbl = tk.Label(chip, text=cat, bg="#e9ecef", fg="#343a40", font=("Segoe UI", 10, "bold"))
            lbl.pack(side=tk.LEFT)

            remove_btn = tk.Button(chip, text="✕", bg="#e9ecef", fg="#6c757d",
                                borderwidth=0, font=("Segoe UI", 9),
                                command=lambda c=cat: self.remove_category(c))
            remove_btn.pack(side=tk.LEFT, padx=(5, 0))