# Tkinter Student Demo

A small desktop application for exploring common Python Tkinter and ttk
controls. It uses only Python's standard library.

## Run

From this folder, run:

```powershell
python main.py
```

Tkinter must be available in your Python installation. The app optionally
displays `logo.png` from this folder.

## Explore

- **Basic controls**: labels, buttons, entry, checkbutton, radiobuttons,
  spinbox, combobox, scale, progressbar, and separator.
- **Lists and tables**: `Text`, `Listbox`, and `Treeview`.
- **Canvas**: draw shapes and respond to mouse clicks.
- **Dialogs**: menu commands, message boxes, and a file chooser.
- **SQLite settings**: persist a student name, theme, font size, and last-opened
  tab between runs.

Preferences are stored in
`~/.tkinter_student_demo/settings.sqlite3` (under your home directory) in a
SQLite table named `settings`. The database is created automatically the first
time the application runs.
