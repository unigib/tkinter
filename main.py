"""A student-friendly showcase of Tkinter and ttk widgets."""

from __future__ import annotations

import sqlite3
import tkinter as tk
from collections.abc import Callable
from contextlib import closing
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_TITLE = "Tkinter CSS51505 Student Demo"
THEMES = ("Light", "Dark")
DEFAULTS = {
    "student_name": "",
    "theme": "Light",
    "font_size": "10",
    "last_tab": "Welcome",
}


class SettingsStore:
    """Persist small application preferences in a local SQLite database."""

    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or (
            Path.home() / ".tkinter_student_demo" / "settings.sqlite3"
        )
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )

    def get_all(self) -> dict[str, str]:
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute("SELECT key, value FROM settings").fetchall()
        return dict(rows)

    def save(self, values: dict[str, str]) -> None:
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.executemany(
                    """
                    INSERT INTO settings (key, value)
                    VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                    """,
                    values.items(),
                )


class TkinterDemo(tk.Tk):
    def __init__(self, database_path: Path | None = None) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x760")
        self.minsize(820, 620)

        self.settings_store = SettingsStore(database_path)
        self.saved_settings = {**DEFAULTS, **self.settings_store.get_all()}
        self.current_theme = (
            self.saved_settings["theme"]
            if self.saved_settings["theme"] in THEMES
            else "Light"
        )
        try:
            self.current_font_size = min(
                16, max(9, int(self.saved_settings["font_size"]))
            )
        except ValueError:
            self.current_font_size = 10

        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        self._create_menu()
        self._create_header()
        self._create_tabs()
        self._apply_theme()
        self._restore_last_tab()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="Save settings", command=self._save_settings)
        file_menu.add_command(label="Choose a file...", command=self._choose_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        demo_menu = tk.Menu(menu_bar, tearoff=False)
        demo_menu.add_command(
            label="Show an information dialog",
            command=lambda: messagebox.showinfo(
                "Tkinter dialog", "This message is shown with tkinter.messagebox."
            ),
        )
        demo_menu.add_command(
            label="Ask a yes/no question",
            command=self._ask_question,
        )
        menu_bar.add_cascade(label="Dialogs", menu=demo_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(
            label="About this demo",
            command=lambda: messagebox.showinfo(
                "About",
                "Explore the tabs to see Tkinter and ttk controls in action.\n"
                "Preferences are stored locally with SQLite.",
            ),
        )
        menu_bar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menu_bar)

    def _create_header(self) -> None:
        self.header = ttk.Frame(self, padding=(18, 12))
        self.header.pack(fill="x")
        self.logo_image: tk.PhotoImage | None = None
        logo_path = Path(__file__).with_name("logo.png")
        if logo_path.exists():
            image = tk.PhotoImage(file=str(logo_path))
            scale = max(1, (image.width() + 159) // 160)
            self.logo_image = image.subsample(scale, scale)
            ttk.Label(self.header, image=self.logo_image).pack(side="left", padx=(0, 14))

        title_area = ttk.Frame(self.header)
        title_area.pack(side="left", fill="x", expand=True)
        ttk.Label(
            title_area, text="Tkinter controls showcase", style="Title.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            title_area,
            text="A hands-on tour of Python's built-in desktop GUI toolkit",
        ).pack(anchor="w", pady=(3, 0))

    def _create_tabs(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        self.tabs: dict[str, ttk.Frame] = {}
        self._add_tab("Welcome", self._build_welcome)
        self._add_tab("Basic controls", self._build_basic_controls)
        self._add_tab("Lists and tables", self._build_lists)
        self._add_tab("Canvas", self._build_canvas)
        self._add_tab("Dialogs", self._build_dialogs)
        self._add_tab("SQLite settings", self._build_settings)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.status_text = tk.StringVar(value="Ready - try a control!")
        ttk.Label(self, textvariable=self.status_text, anchor="w", padding=(14, 5)).pack(
            fill="x"
        )

    def _add_tab(self, title: str, builder: Callable[[ttk.Frame], None]) -> None:
        frame = ttk.Frame(self.notebook, padding=18)
        self.tabs[title] = frame
        self.notebook.add(frame, text=title)
        builder(frame)

    @staticmethod
    def _section(parent: ttk.Frame, title: str, description: str) -> None:
        ttk.Label(parent, text=title, style="Section.TLabel").pack(anchor="w")
        ttk.Label(parent, text=description, wraplength=850).pack(
            anchor="w", pady=(3, 14)
        )

    def _build_welcome(self, parent: ttk.Frame) -> None:
        self._section(
            parent,
            "Welcome!",
            "This small application is a gallery of common Tkinter and ttk controls. "
            "Use the tabs to interact with each widget and read the notes as you go.",
        )
        cards = ttk.LabelFrame(parent, text="What you will find", padding=14)
        cards.pack(fill="x", pady=(0, 16))
        descriptions = (
            "Basic controls: labels, buttons, entries, checkboxes, radio buttons, "
            "sliders, spinboxes, and dropdowns.",
            "Lists and tables: editable text, listboxes, and a sortable-looking "
            "Treeview data table.",
            "Canvas: draw shapes and see how mouse events can be handled.",
            "Dialogs: menus, file selection, and message boxes.",
            "SQLite settings: save a name, color theme, and font size between runs.",
        )
        for description in descriptions:
            ttk.Label(cards, text=f"• {description}", wraplength=850).pack(
                anchor="w", pady=3
            )
        ttk.Label(
            parent,
            text="Tip: change a control, then watch the status line at the bottom.",
            style="Tip.TLabel",
        ).pack(anchor="w", pady=8)

    def _build_basic_controls(self, parent: ttk.Frame) -> None:
        self._section(
            parent,
            "Basic controls",
            "These widgets are the building blocks of many desktop forms.",
        )
        form = ttk.LabelFrame(parent, text="A simple form", padding=14)
        form.pack(fill="x")

        ttk.Label(form, text="Entry (type your name):").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=6
        )
        self.name_entry = ttk.Entry(form, width=34)
        self.name_entry.grid(row=0, column=1, sticky="w", pady=6)
        ttk.Button(form, text="Greet me", command=self._greet).grid(
            row=0, column=2, padx=10, pady=6
        )

        self.subscribe_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            form,
            text="Checkbutton: receive learning tips",
            variable=self.subscribe_var,
            command=lambda: self._set_status(
                f"Learning tips: {'on' if self.subscribe_var.get() else 'off'}"
            ),
        ).grid(row=1, column=1, columnspan=2, sticky="w", pady=6)

        self.level_var = tk.StringVar(value="Beginner")
        radio_frame = ttk.Frame(form)
        radio_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=6)
        ttk.Label(form, text="Radiobuttons: experience").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=6
        )
        for level in ("Beginner", "Intermediate", "Advanced"):
            ttk.Radiobutton(
                radio_frame,
                text=level,
                value=level,
                variable=self.level_var,
                command=lambda: self._set_status(
                    f"Selected level: {self.level_var.get()}"
                ),
            ).pack(side="left", padx=(0, 10))

        ttk.Label(form, text="Spinbox: choose a year").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=6
        )
        self.year_spin = ttk.Spinbox(form, from_=1, to=4, width=8)
        self.year_spin.set("1")
        self.year_spin.grid(row=3, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Combobox: choose a course").grid(
            row=4, column=0, sticky="w", padx=(0, 10), pady=6
        )
        self.course_combo = ttk.Combobox(
            form,
            values=("Python", "Web development", "Data science", "Robotics"),
            state="readonly",
            width=31,
        )
        self.course_combo.current(0)
        self.course_combo.grid(row=4, column=1, sticky="w", pady=6)
        self.course_combo.bind(
            "<<ComboboxSelected>>",
            lambda _event: self._set_status(
                f"Course selected: {self.course_combo.get()}"
            ),
        )

        ttk.Label(form, text="Scale: set the progress").grid(
            row=5, column=0, sticky="w", padx=(0, 10), pady=6
        )
        self.progress = ttk.Progressbar(
            form, length=280, mode="determinate", maximum=100
        )
        self.progress.grid(row=5, column=1, sticky="w", pady=6)
        ttk.Scale(
            form,
            from_=0,
            to=100,
            command=lambda value: self.progress.configure(value=float(value)),
        ).grid(row=5, column=2, sticky="ew", padx=10, pady=6)
        ttk.Separator(parent).pack(fill="x", pady=18)
        ttk.Label(
            parent,
            text="Also included: ttk.Label, ttk.Frame, ttk.LabelFrame, "
            "ttk.Separator, ttk.Progressbar, and ttk.Scale.",
            wraplength=850,
        ).pack(anchor="w")

    def _build_lists(self, parent: ttk.Frame) -> None:
        self._section(
            parent,
            "Lists and tables",
            "Tkinter's Text and Listbox widgets pair naturally with ttk.Treeview "
            "for editable text, selections, and tabular data.",
        )
        columns = ttk.Frame(parent)
        columns.pack(fill="both", expand=True)

        text_group = ttk.LabelFrame(columns, text="Text widget", padding=10)
        text_group.pack(side="left", fill="both", expand=True, padx=(0, 8))
        self.notes_text = tk.Text(text_group, height=8, width=35, wrap="word")
        self.notes_text.pack(fill="both", expand=True)
        self.notes_text.insert(
            "1.0", "This is a multiline Text widget.\nTry typing or editing this note."
        )

        list_group = ttk.LabelFrame(columns, text="Listbox", padding=10)
        list_group.pack(side="left", fill="both", expand=True, padx=(8, 0))
        self.topic_list = tk.Listbox(list_group, height=8, exportselection=False)
        for topic in (
            "Widgets",
            "Events",
            "Layouts",
            "Variables",
            "SQLite",
            "Canvas drawing",
        ):
            self.topic_list.insert("end", topic)
        self.topic_list.pack(fill="both", expand=True)
        self.topic_list.bind("<<ListboxSelect>>", self._on_topic_selected)

        table_group = ttk.LabelFrame(parent, text="Treeview data table", padding=10)
        table_group.pack(fill="both", expand=True, pady=(16, 0))
        self.table = ttk.Treeview(
            table_group,
            columns=("course", "weeks", "level"),
            show="headings",
            height=5,
        )
        for key, label, width in (
            ("course", "Course", 220),
            ("weeks", "Weeks", 100),
            ("level", "Level", 160),
        ):
            self.table.heading(key, text=label)
            self.table.column(key, width=width, anchor="w")
        for item in (
            ("Python basics", "6", "Beginner"),
            ("GUI programming", "4", "Intermediate"),
            ("Data projects", "8", "Intermediate"),
        ):
            self.table.insert("", "end", values=item)
        self.table.pack(fill="both", expand=True)

    def _build_canvas(self, parent: ttk.Frame) -> None:
        self._section(
            parent,
            "Canvas drawing",
            "A Canvas can display shapes, text, and images. Click inside the "
            "canvas to add a dot; use the buttons to add a shape or clear it.",
        )
        buttons = ttk.Frame(parent)
        buttons.pack(fill="x", pady=(0, 10))
        ttk.Button(buttons, text="Add a rectangle", command=self._draw_rectangle).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(buttons, text="Clear canvas", command=self._clear_canvas).pack(
            side="left"
        )
        self.canvas = tk.Canvas(
            parent, height=360, background="white", highlightthickness=1
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._draw_dot)
        self.canvas.create_text(
            20,
            20,
            anchor="nw",
            text="Click anywhere to draw a dot.",
            fill="#333333",
        )
        self.canvas.create_oval(90, 100, 190, 200, fill="#7bc8a4", outline="")
        self.canvas.create_rectangle(
            250, 100, 390, 200, fill="#80b7e8", outline="#3278ad", width=2
        )
        self.canvas.create_line(460, 100, 560, 200, fill="#d87955", width=4)
        self.canvas.create_text(
            650, 150, text="Canvas text", fill="#333333", font=("TkDefaultFont", 14)
        )

    def _build_dialogs(self, parent: ttk.Frame) -> None:
        self._section(
            parent,
            "Menus and dialogs",
            "Use the File and Dialogs menus at the top of the window, or try "
            "the buttons below. Dialogs return values your program can act on.",
        )
        group = ttk.LabelFrame(parent, text="Try a dialog", padding=16)
        group.pack(anchor="nw", fill="x")
        ttk.Button(
            group,
            text="Show information",
            command=lambda: messagebox.showinfo(
                "Information", "This is an information message."
            ),
        ).pack(anchor="w", pady=5)
        ttk.Button(
            group,
            text="Ask yes or no",
            command=self._ask_question,
        ).pack(anchor="w", pady=5)
        ttk.Button(
            group,
            text="Choose a file",
            command=self._choose_file,
        ).pack(anchor="w", pady=5)
        self.file_label = ttk.Label(parent, text="No file selected.")
        self.file_label.pack(anchor="w", pady=14)
        ttk.Label(
            parent,
            text="Other common dialog types include askyesno, askstring, "
            "askopenfilename, and asksaveasfilename.",
            wraplength=850,
        ).pack(anchor="w")

    def _build_settings(self, parent: ttk.Frame) -> None:
        self._section(
            parent,
            "Settings stored with SQLite",
            "Preferences are saved in a small SQLite database in your home "
            "folder. Save them here, or use File > Save settings.",
        )
        form = ttk.LabelFrame(parent, text="Preferences", padding=14)
        form.pack(fill="x")

        ttk.Label(form, text="Student name:").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=6
        )
        self.settings_name = ttk.Entry(form, width=32)
        self.settings_name.insert(0, self.saved_settings["student_name"])
        self.settings_name.grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Color theme:").grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=6
        )
        self.theme_var = tk.StringVar(value=self.current_theme)
        ttk.OptionMenu(form, self.theme_var, self.current_theme, *THEMES).grid(
            row=1, column=1, sticky="w", pady=6
        )

        ttk.Label(form, text="Font size:").grid(
            row=2, column=0, sticky="w", padx=(0, 12), pady=6
        )
        self.font_size_var = tk.IntVar(value=self.current_font_size)
        ttk.Spinbox(
            form,
            from_=9,
            to=16,
            textvariable=self.font_size_var,
            width=8,
        ).grid(row=2, column=1, sticky="w", pady=6)
        ttk.Button(form, text="Save preferences", command=self._save_settings).grid(
            row=3, column=1, sticky="w", pady=(12, 4)
        )

        db_group = ttk.LabelFrame(parent, text="Saved settings table", padding=10)
        db_group.pack(fill="both", expand=True, pady=(16, 0))
        self.settings_table = ttk.Treeview(
            db_group, columns=("key", "value"), show="headings", height=6
        )
        self.settings_table.heading("key", text="Setting")
        self.settings_table.heading("value", text="Value")
        self.settings_table.column("key", width=180, anchor="w")
        self.settings_table.column("value", width=500, anchor="w")
        self.settings_table.pack(fill="both", expand=True)
        self._refresh_settings_table()

    def _apply_theme(self) -> None:
        dark = self.current_theme == "Dark"
        background = "#24272e" if dark else "#f4f6f8"
        foreground = "#f3f4f6" if dark else "#20252b"
        panel = "#30343d" if dark else "#ffffff"
        self.configure(background=background)
        self.style.configure(".", font=("TkDefaultFont", self.current_font_size))
        self.style.configure("TFrame", background=background)
        self.style.configure("TLabel", background=background, foreground=foreground)
        self.style.configure(
            "Title.TLabel", font=("TkDefaultFont", self.current_font_size + 8, "bold")
        )
        self.style.configure(
            "Section.TLabel",
            font=("TkDefaultFont", self.current_font_size + 3, "bold"),
        )
        self.style.configure(
            "Tip.TLabel",
            foreground="#246b48" if not dark else "#93d6ae",
            font=("TkDefaultFont", self.current_font_size, "italic"),
        )
        self.style.configure("TLabelframe", background=background, foreground=foreground)
        self.style.configure(
            "TLabelframe.Label", background=background, foreground=foreground
        )
        self.style.configure(
            "TNotebook", background=background, tabmargins=(2, 6, 2, 0)
        )
        self.style.configure(
            "TNotebook.Tab",
            padding=(10, 6),
            background=panel,
            foreground=foreground,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", background)],
            foreground=[("selected", foreground)],
        )
        self.style.configure(
            "Treeview",
            background=panel,
            fieldbackground=panel,
            foreground=foreground,
            rowheight=self.current_font_size + 12,
        )
        self.style.configure(
            "Treeview.Heading", background=background, foreground=foreground
        )
        if hasattr(self, "notes_text"):
            self.notes_text.configure(
                background=panel,
                foreground=foreground,
                insertbackground=foreground,
                font=("TkDefaultFont", self.current_font_size),
            )
            self.topic_list.configure(
                background=panel,
                foreground=foreground,
                selectbackground="#4679a8",
                font=("TkDefaultFont", self.current_font_size),
            )
            self.canvas.configure(background=panel)

    def _restore_last_tab(self) -> None:
        tab_name = self.saved_settings.get("last_tab", "Welcome")
        if tab_name in self.tabs:
            self.notebook.select(self.tabs[tab_name])

    def _save_settings(self) -> None:
        try:
            font_size = min(16, max(9, int(self.font_size_var.get())))
            theme = self.theme_var.get()
            if theme not in THEMES:
                raise ValueError("Choose either the Light or Dark theme.")
            values = {
                "student_name": self.settings_name.get().strip(),
                "theme": theme,
                "font_size": str(font_size),
                "last_tab": self.notebook.tab(self.notebook.select(), "text"),
            }
            self.settings_store.save(values)
        except (sqlite3.Error, ValueError, tk.TclError) as error:
            messagebox.showerror("Could not save settings", str(error))
            return

        self.current_theme = theme
        self.current_font_size = font_size
        self._apply_theme()
        self._refresh_settings_table()
        self._set_status(f"Settings saved to {self.settings_store.database_path}")

    def _refresh_settings_table(self) -> None:
        for item in self.settings_table.get_children():
            self.settings_table.delete(item)
        for key, value in sorted(self.settings_store.get_all().items()):
            self.settings_table.insert("", "end", values=(key, value))

    def _on_tab_changed(self, _event: tk.Event[tk.Misc]) -> None:
        if hasattr(self, "settings_name"):
            self.settings_store.save(
                {"last_tab": self.notebook.tab(self.notebook.select(), "text")}
            )

    def _on_close(self) -> None:
        if hasattr(self, "settings_name"):
            self.settings_store.save(
                {"last_tab": self.notebook.tab(self.notebook.select(), "text")}
            )
        self.destroy()

    def _greet(self) -> None:
        name = self.name_entry.get().strip() or "student"
        messagebox.showinfo("Hello!", f"Hello, {name}!")
        self._set_status(f"Greeted {name}")

    def _ask_question(self) -> None:
        answer = messagebox.askyesno("A question", "Are you enjoying this demo?")
        self._set_status("You clicked Yes." if answer else "You clicked No.")

    def _choose_file(self) -> None:
        filename = filedialog.askopenfilename(title="Choose a file")
        if filename:
            if hasattr(self, "file_label"):
                self.file_label.configure(text=f"Selected: {filename}")
            self._set_status(f"Selected {Path(filename).name}")
        else:
            self._set_status("File selection cancelled")

    def _on_topic_selected(self, _event: tk.Event[tk.Misc]) -> None:
        selection = self.topic_list.curselection()
        if selection:
            self._set_status(f"Topic selected: {self.topic_list.get(selection[0])}")

    def _draw_dot(self, event: tk.Event[tk.Canvas]) -> None:
        radius = 6
        self.canvas.create_oval(
            event.x - radius,
            event.y - radius,
            event.x + radius,
            event.y + radius,
            fill="#d87955",
            outline="",
        )

    def _draw_rectangle(self) -> None:
        self.canvas.create_rectangle(
            70, 250, 220, 320, fill="#f3c969", outline="#bd8a20", width=2
        )
        self._set_status("Rectangle added to the canvas")

    def _clear_canvas(self) -> None:
        self.canvas.delete("all")
        self._set_status("Canvas cleared")

    def _set_status(self, message: str) -> None:
        self.status_text.set(message)


if __name__ == "__main__":
    TkinterDemo().mainloop()
