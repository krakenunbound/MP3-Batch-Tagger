#!/usr/bin/env python3
"""

                                              ,
                                            ,o
                                            :o
                   _....._                  `:o
                 .'       ``-.                \o
                /  _      _   \                \o
               :  /*\    /*\   )                ;o
               |  \_/    \_/   /                ;o
               (       U      /                 ;o
                \  (\_____/) /                  /o
                 \   \_m_/  (                  /o
                  \         (                ,o:
                  )          \,           .o;o'           ,o'o'o.
                ./          /\o;o,,,,,;o;o;''         _,-o,-'''-o:o.
 .             ./o./)        \    'o'o'o''         _,-'o,o'         o
 o           ./o./ /       .o \.              __,-o o,o'
 \o.       ,/o /  /o/)     | o o'-..____,,-o'o o_o-'
 `o:o...-o,o-' ,o,/ |     \   'o.o_o_o_o,o--''
 .,  ``o-o'  ,.oo/   'o /\.o`.
 `o`o-....o'o,-'   /o /   \o \.                       ,o..         o
   ``o-o.o--      /o /      \o.o--..          ,,,o-o'o.--o:o:o,,..:o
                 (oo(          `--o.o`o---o'o'o,o,-'''        o'o'o
                  \ o\              ``-o-o''''
   ,-o;o           \o \
  /o/               )o )
 (o(               /o /                |
  \o\.       ...-o'o /             \   |
    \o`o`-o'o o,o,--'       ~~~~~~~~\~~|~~~~~The Kraken 2025~~~~~~~~~~~~~~~~~~~~~~~
      ```o--'''                       \| /
                                       |/
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                       |
 ~~~~~~~ August 2025 with Grok4 & ChatGPT5 (mostly Grok)~~~~~~~~~~~~~~~~~~~~~~~~~~
 
 Batch MP3 Metadata Tagger with GUI, Profile Save/Load, Auto-Numbering, Dark Theme & Top Banner
This script provides a Tkinter-based GUI for entering ID3 metadata
and applying it to all .mp3 files in a selected directory. It supports:
  - Saving/loading a JSON profile of metadata fields
  - Automatically numbering track numbers based on file count
  - A built-in dark color theme
  - Displaying a banner image at the top (32:9 aspect)
  - Optional immersive dark title-bar on Windows 10/11

Instructions for Users:
1. Install Python:
   - Download the latest Python version from https://www.python.org/downloads/.
   - During installation, check "Add Python to PATH" for easy command-line access.
   - Verify installation by opening a terminal/command prompt and typing 'python --version'.

2. Install Dependencies:
   - Open a terminal/command prompt.
   - Run: pip install mutagen pillow
   - This installs the required libraries for tag editing and image handling.

3. How to Run:
   - Save this script as mp3tag.py (or mp3tag.pyw to suppress console window on Windows).
   - Place banner images (named banner1.png, banner2.png, etc.) in the same directory for random top banners (optional).
   - Run: python mp3tag.py (or double-click mp3tag.pyw on Windows).
   - Select a music folder, fill metadata fields, and click "Tag Files" to apply tags.

Dependencies:
    pip install mutagen pillow
Usage:
    python mp3tag.py
"""

import os
import threading
import json
import random
import re
import ctypes
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from PIL import Image, ImageTk
from mutagen.id3 import (
    ID3, TPE1, TPE2, TDRC, TRCK, TCON,
    TPUB, TSSE, WXXX, TCOP, TCOM,
    TPE3, TXXX, TALB, APIC
)
from mutagen.wave import WAVE
from mutagen import MutagenError
import wave # Standard library for WAV handling
import struct
from io import BytesIO
import shutil # For safe file replace
# Windows DWM attribute for dark mode
DWMWA_USE_IMMERSIVE_DARK_MODE = 20 # Windows 10 1903+, Win11
# Default profile path
PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".mp3_tagger_profile.json")
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    def show_tooltip(self, event=None):
        x, y = self.widget.winfo_pointerxy()
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+15}+{y+15}")
        label = tk.Label(self.tooltip, text=self.text, bg="#ffffe0", fg="#000000", relief="solid", borderwidth=1, padx=5, pady=3)
        label.pack()
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
class MP3TaggerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        # Theme colors
        self.bg_color = "#2e2e2e"
        self.fg_color = "#ffffff"
        self.entry_bg = "#3e3e3e"
        self.button_bg = "#444444"
        self.button_fg = "#ffffff"
        # Window setup
        self.title("MP3/WAV Batch Tagger")
        self.geometry("600x820")
        self.minsize(480, 580)
        self.configure(bg=self.bg_color)
        # ttk dark style
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TButton', background=self.button_bg, foreground=self.button_fg)
        self.style.configure('TEntry', fieldbackground=self.entry_bg, foreground=self.fg_color)
        self.style.configure('TCheckbutton', background=self.bg_color, foreground=self.fg_color)
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('Horizontal.TProgressbar', troughcolor=self.entry_bg, background='#888888')
        # Immersive dark title-bar on Windows
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            val = ctypes.c_int(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(val),
                ctypes.sizeof(val)
            )
        except Exception:
            pass
        # Menu bar
        self._build_menubar()
        # Top banner (resizes with window width)
        self.banner_img_orig = self._load_banner_image()
        if self.banner_img_orig:
            self._render_banner()
        self.bind('<Configure>', self._on_resize)
        # Main frame
        main = ttk.Frame(self)
        main.pack(fill='both', expand=True)
        main.grid_columnconfigure(0, weight=1)
        # Directory
        dir_frame = ttk.Frame(main)
        dir_frame.grid(row=0, column=0, sticky='ew', pady=6, padx=8)
        ttk.Label(dir_frame, text="Music Folder:").pack(side='left')
        self.dir_label = ttk.Label(dir_frame, text="(none selected)")
        self.dir_label.pack(side='left', fill='x', expand=True, padx=6)
        self.dir_browse_btn = ttk.Button(dir_frame, text="Browse…", command=self.select_directory)
        self.dir_browse_btn.pack(side='right')
        Tooltip(self.dir_browse_btn, "Select a folder containing MP3/WAV files to batch tag.")
        # Profile row
        prof = ttk.Frame(main)
        prof.grid(row=1, column=0, sticky='ew', padx=8, pady=2)
        load_prof_btn = ttk.Button(prof, text="Load Profile", command=self.load_profile)
        load_prof_btn.pack(side='left', padx=4)
        Tooltip(load_prof_btn, "Load saved metadata values from a JSON profile file.")
        save_prof_btn = ttk.Button(prof, text="Save Profile", command=self.save_profile)
        save_prof_btn.pack(side='left', padx=4)
        Tooltip(save_prof_btn, "Save current metadata values to a JSON profile file for reuse.")
        reset_btn = ttk.Button(prof, text="Reset Fields", command=self.reset_fields)
        reset_btn.pack(side='left', padx=4)
        Tooltip(reset_btn, "Clear all metadata fields to blank.")
        # Fields
        fields = [
            ("Contributing Artist", "TPE1"),
            ("Album Artist", "TPE2"),
            ("Year", "TDRC"),
            ("Track Number", "TRCK"),
            ("Genre", "TCON"),
            ("Publisher", "TPUB"),
            ("Encoded by", "TSSE"),
            ("Author URL", "WXXX"),
            ("Copyright", "TCOP"),
            ("Composers", "TCOM"),
            ("Conductors", "TPE3"),
            ("Group Description", "TXXX:Group Description"),
            ("Mood", "TXXX:Mood"),
            ("Album", "TALB"),
            ("Parental Rating Reason", "TXXX:Parental Rating Reason"),
        ]
        self.vars = {}
        form = ttk.Frame(main)
        form.grid(row=2, column=0, sticky='ew', padx=8)
        for label_text, tag_key in fields:
            row = ttk.Frame(form)
            row.pack(fill='x', pady=2)
            ttk.Label(row, text=label_text+":", width=22, anchor='w').pack(side='left')
            var = tk.StringVar()
            ttk.Entry(row, textvariable=var, width=48).pack(side='left', fill='x', expand=True)
            self.vars[tag_key] = var
        # Options - streamlined into multiple rows
        opts = ttk.Frame(main)
        opts.grid(row=3, column=0, sticky='ew', padx=8, pady=6)
        # Row 1: Auto-number
        opt_row1 = ttk.Frame(opts)
        opt_row1.pack(fill='x')
        self.auto_number = tk.BooleanVar(value=False)
        auto_num_chk = ttk.Checkbutton(opt_row1, text="Auto-number tracks", variable=self.auto_number)
        auto_num_chk.pack(side='left', padx=(0,8))
        Tooltip(auto_num_chk, "Automatically assign track numbers based on file order (e.g., 1/10, 2/10).")
        # Row 2: Number options and Embed
        opt_row2 = ttk.Frame(opts)
        opt_row2.pack(fill='x')
        self.only_fill_missing = tk.BooleanVar(value=False)
        missing_chk = ttk.Checkbutton(opt_row2, text="Only fill missing", variable=self.only_fill_missing)
        missing_chk.pack(side='left', padx=(0,8))
        Tooltip(missing_chk, "When auto-numbering, only set track number if it's missing in the file.")
        ttk.Label(opt_row2, text="Start at:").pack(side='left')
        self.track_offset = tk.IntVar(value=1)
        self.offset_spin = ttk.Spinbox(opt_row2, from_=1, to=9999, textvariable=self.track_offset, width=5)
        self.offset_spin.pack(side='left', padx=(4,12))
        Tooltip(self.offset_spin, "Starting number for auto-numbering (e.g., 1 for 1/total, 2 for 2/total).")
        self.embed_cover = tk.BooleanVar(value=True)
        embed_chk = ttk.Checkbutton(opt_row2, text="Embed cover", variable=self.embed_cover)
        embed_chk.pack(side='left', padx=(0,8))
        Tooltip(embed_chk, "Embed album art (cover.jpg/png in folder or selected) into files if found.")
        self.cover_pick_btn = ttk.Button(opt_row2, text="Pick Cover…", command=self.select_batch_cover)
        self.cover_pick_btn.pack(side='left', padx=(4,8))
        Tooltip(self.cover_pick_btn, "Select a custom cover image to embed in all files (overrides folder cover.jpg).")
        # Row 3: Advanced
        opt_row3 = ttk.Frame(opts)
        opt_row3.pack(fill='x')
        self.verify_writes = tk.BooleanVar(value=True)
        verify_chk = ttk.Checkbutton(opt_row3, text="Verify save", variable=self.verify_writes)
        verify_chk.pack(side='left', padx=(0,8))
        Tooltip(verify_chk, "After saving, read back tags to confirm they were written correctly.")
        self.force_v23 = tk.BooleanVar(value=True)
        v23_chk = ttk.Checkbutton(opt_row3, text="ID3v2.3", variable=self.force_v23)
        v23_chk.pack(side='left', padx=(0,8))
        Tooltip(v23_chk, "Use ID3v2.3 format for compatibility with older players/Windows (v2.4 may not work everywhere).")
        # Single-file mode
        single = ttk.Frame(main)
        single.grid(row=4, column=0, sticky='ew', padx=8, pady=(0,6))
        self.single_mode = tk.BooleanVar(value=False)
        single_chk = ttk.Checkbutton(single, text="Single-file mode", variable=self.single_mode, command=self._toggle_single_mode)
        single_chk.pack(side='left', padx=(0,8))
        Tooltip(single_chk, "Tag a single file instead of a folder (disables auto-numbering).")
        self.single_file_label = ttk.Label(single, text="(no file)")
        self.single_pick_btn = ttk.Button(single, text="Pick File…", command=self.select_single_file)
        self.single_cover_btn = ttk.Button(single, text="Pick Cover…", command=self.select_single_cover)
        self.single_pick_btn.pack(side='left', padx=(0,8))
        Tooltip(self.single_pick_btn, "Select a single MP3/WAV file to tag.")
        self.single_cover_btn.pack(side='left', padx=(0,8))
        Tooltip(self.single_cover_btn, "Select a custom cover image for this single file.")
        self.single_file_label.pack(side='left', padx=(4,0))
        self.single_path = None
        self.single_cover = (None, None)
        self.batch_cover = (None, None)
        # Progress + actions
        act = ttk.Frame(main)
        act.grid(row=5, column=0, sticky='ew', padx=8)
        self.progress = ttk.Progressbar(act, orient='horizontal', mode='determinate', length=260)
        self.progress.pack(side='left', padx=(0,8))
        self.run_btn = ttk.Button(act, text="Tag Files", command=self.start_tagging, width=16)
        self.run_btn.pack(side='left')
        Tooltip(self.run_btn, "Start tagging the selected folder or file.")
        self.cancel_btn = ttk.Button(act, text="Cancel", command=self.cancel_tagging, width=10)
        self.cancel_btn.pack(side='left', padx=(8,0))
        self.cancel_btn.state(['disabled'])
        Tooltip(self.cancel_btn, "Cancel the ongoing tagging process.")
        # Log
        log_frame = ttk.Frame(main)
        log_frame.grid(row=6, column=0, sticky='nsew', padx=8, pady=8)
        main.grid_rowconfigure(6, weight=1)
        self.log = ScrolledText(log_frame, height=8, state='disabled', bg=self.entry_bg, fg=self.fg_color)
        self.log.pack(fill='both', expand=True)
        # Auto-load last profile
        if os.path.exists(PROFILE_PATH):
            self.load_profile(PROFILE_PATH, silent=True)
        # Controls collection for enable/disable
        self._collect_controls()
    def _build_menubar(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open Folder…", command=self.select_directory)
        file_menu.add_command(label="Open File…", command=self.select_single_file)
        file_menu.add_separator()
        file_menu.add_command(label="Load Profile…", command=self.load_profile)
        file_menu.add_command(label="Save Profile…", command=self.save_profile)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=lambda: messagebox.showinfo(
            "About Batch Tagger",
            "MP3/WAV Batch Tagger — built with ❤️ for The Kraken"))
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)
    def _load_banner_image(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        imgs = [f for f in os.listdir(script_dir) if re.match(r'banner\d+\.png$', f, flags=re.IGNORECASE)]
        if not imgs:
            return None
        choice = random.choice(imgs)
        path = os.path.join(script_dir, choice)
        try:
            return Image.open(path)
        except Exception as e:
            print(f"Banner load failed {path}: {e}")
            return None
    def _render_banner(self):
        if not self.banner_img_orig:
            return
        w = self.winfo_width() or 600
        h = max(80, int(w * 9 / 32)) # 32:9 strip
        img_resized = self.banner_img_orig.resize((w, h), Image.LANCZOS)
        self.banner_photo = ImageTk.PhotoImage(img_resized)
        if not hasattr(self, 'banner_label'):
            self.banner_label = ttk.Label(self, image=self.banner_photo)
            self.banner_label.pack(fill='x')
        else:
            self.banner_label.configure(image=self.banner_photo)
            self.banner_label.image = self.banner_photo
    def _on_resize(self, event):
        if event.widget is self:
            self._render_banner()
    def _collect_controls(self):
        self._controls = []
        for child in self.winfo_children():
            if getattr(self, 'banner_label', None) is child:
                continue
            if isinstance(child, (ttk.Frame,)):
                for sub in child.winfo_children():
                    if isinstance(sub, (ttk.Button, ttk.Entry, ttk.Checkbutton, ttk.Spinbox)):
                        self._controls.append(sub)
                    elif isinstance(sub, (ttk.Frame,)):
                        for subsub in sub.winfo_children():
                            if isinstance(subsub, (ttk.Button, ttk.Entry, ttk.Checkbutton, ttk.Spinbox)):
                                self._controls.append(subsub)
    def _set_controls_enabled(self, enabled: bool):
        for c in self._controls:
            try:
                if enabled:
                    c.state(['!disabled'])
                else:
                    c.state(['disabled'])
            except Exception:
                pass
        if enabled:
            self.cancel_btn.state(['disabled'])
            self.run_btn.state(['!disabled'])
        else:
            self.cancel_btn.state(['!disabled'])
            self.run_btn.state(['disabled'])
    def _toggle_single_mode(self):
        on = self.single_mode.get()
        for w in (self.single_pick_btn, self.single_cover_btn):
            try:
                w.state(['!disabled' if on else 'disabled'])
            except Exception:
                pass
        for w in (self.dir_browse_btn, self.offset_spin, self.cover_pick_btn):
            try:
                w.state(['disabled' if on else '!disabled'])
            except Exception:
                pass
        for chk in (self.only_fill_missing, self.auto_number):
            chk.set(False if on else chk.get())
    def select_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder = folder
            self.dir_label.config(text=folder)
            if 'TALB' in self.vars and not self.vars['TALB'].get():
                self.vars['TALB'].set(os.path.basename(folder))
    def select_single_file(self):
        types = [('Audio', '*.mp3 *.wav'), ('MP3', '*.mp3'), ('WAV', '*.wav')]
        path = filedialog.askopenfilename(filetypes=types, title='Choose audio file')
        if path:
            self.single_path = path
            self.single_file_label.config(text=os.path.basename(path))
            if 'TALB' in self.vars and not self.vars['TALB'].get():
                self.vars['TALB'].set(os.path.basename(os.path.dirname(path)))
    def select_single_cover(self):
        types = [('Images', '*.jpg *.jpeg *.png'), ('JPEG', '*.jpg *.jpeg'), ('PNG', '*.png')]
        path = filedialog.askopenfilename(filetypes=types, title='Choose cover image')
        if path:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                mime = 'image/png' if path.lower().endswith('png') else 'image/jpeg'
                self.single_cover = (data, mime)
                self.log_message(f"Selected cover: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror('Cover Error', f'Failed to read image: {e}')
    def select_batch_cover(self):
        types = [('Images', '*.jpg *.jpeg *.png'), ('JPEG', '*.jpg *.jpeg'), ('PNG', '*.png')]
        path = filedialog.askopenfilename(filetypes=types, title='Choose cover image for all')
        if path:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                mime = 'image/png' if path.lower().endswith('png') else 'image/jpeg'
                self.batch_cover = (data, mime)
                self.log_message(f"Selected cover for batch: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror('Cover Error', f'Failed to read image: {e}')
    def log_message(self, message):
        def _append():
            self.log.config(state='normal')
            self.log.insert('end', message + '\n')
            self.log.yview('end')
            self.log.config(state='disabled')
        self.after(0, _append)
    def start_tagging(self):
        if self.single_mode.get():
            if not self.single_path or not os.path.isfile(self.single_path):
                messagebox.showerror('Error', 'Pick a valid audio file for single-file mode.')
                return
        else:
            if not hasattr(self, 'folder') or not os.path.isdir(self.folder):
                messagebox.showerror('Error', 'Select a valid music folder first.')
                return
        self.progress['value'] = 0
        self.cancel_event = threading.Event()
        self._set_controls_enabled(False)
        self.log.config(state='normal'); self.log.delete('1.0', 'end'); self.log.config(state='disabled')
        threading.Thread(target=self._worker_apply, daemon=True).start()
    def cancel_tagging(self):
        if hasattr(self, 'cancel_event'):
            self.cancel_event.set()
            self.log_message("Cancellation requested… finishing current file.")
    def _gather_files(self):
        if self.single_mode.get() and self.single_path:
            return [self.single_path]
        files = []
        for root, _, names in os.walk(self.folder):
            for f in names:
                ext = os.path.splitext(f)[1].lower()
                if ext in ('.mp3', '.wav'):
                    files.append(os.path.join(root, f))
        files.sort(key=lambda p: p.lower())
        return files
    def _worker_apply(self):
        try:
            files = self._gather_files()
            total = len(files)
            if total == 0:
                self.log_message("No audio files found.")
                self._finish_worker()
                return
            self.after(0, lambda: (self.progress.configure(maximum=total), None))
            base_md = {k: v.get().strip() for k, v in self.vars.items()}
            auto = self.auto_number.get()
            fill_missing_only = self.only_fill_missing.get()
            offset = max(1, int(self.track_offset.get() or 1))
            embed = self.embed_cover.get()
            cover_bytes, cover_mime = (None, None)
            if self.single_mode.get():
                if self.single_cover[0]:
                    cover_bytes, cover_mime = self.single_cover
                elif embed:
                    cover_bytes, cover_mime = self._find_cover_art(os.path.dirname(self.single_path))
            else:
                if self.batch_cover[0]:
                    cover_bytes, cover_mime = self.batch_cover
                elif embed:
                    cover_bytes, cover_mime = self._find_cover_art(self.folder)
            if cover_bytes:
                self.log_message(f"Cover art found ({cover_mime}); will embed.")
            elif embed:
                self.log_message("No cover art found to embed.")
            for i, path in enumerate(files, start=1):
                if self.cancel_event.is_set():
                    self.log_message("Cancelled by user.")
                    break
                md = dict(base_md)
                if auto and not self.single_mode.get():
                    if fill_missing_only:
                        try:
                            if path.lower().endswith('.wav'):
                                existing = (WAVE(path).tags or ID3()).get('TRCK')
                            else:
                                existing = ID3(path).get('TRCK')
                            has_track = bool(existing and getattr(existing, 'text', [''])[0])
                        except Exception:
                            has_track = False
                        if not has_track:
                            md['TRCK'] = f"{offset + i - 1}/{total + offset - 1}"
                    else:
                        md['TRCK'] = f"{offset + i - 1}/{total + offset - 1}"
                try:
                    self.apply_meta(path, md, cover=(cover_bytes, cover_mime))
                    self.log_message(f"[{i}/{total}] Tagged: {os.path.basename(path)}")
                except (MutagenError, OSError, ValueError) as e:
                    self.log_message(f"Error tagging {os.path.basename(path)}: {type(e).__name__} - {e}")
                except Exception as e:
                    self.log_message(f"Unexpected error tagging {os.path.basename(path)}: {type(e).__name__} - {e}")
                finally:
                    self.after(0, lambda v=i: self.progress.configure(value=v))
            self._finish_worker()
        except Exception as e:
            self.log_message(f"Fatal error: {e}")
            self._finish_worker()
    def _finish_worker(self):
        self.after(0, lambda: (self._set_controls_enabled(True), messagebox.showinfo("Done", "Tagging complete!")))
    def apply_meta(self, file_path, metadata, cover=(None, None)):
        ext = os.path.splitext(file_path)[1].lower()
        id3 = ID3()
        def set_frame(key, frame):
            id3.delall(key)
            id3.add(frame)
        # Standard frames
        if metadata.get('TPE1'): set_frame('TPE1', TPE1(encoding=3, text=[metadata['TPE1']]))
        if metadata.get('TPE2'): set_frame('TPE2', TPE2(encoding=3, text=[metadata['TPE2']]))
        if metadata.get('TDRC'): set_frame('TDRC', TDRC(encoding=3, text=[metadata['TDRC']]))
        if metadata.get('TRCK'): set_frame('TRCK', TRCK(encoding=3, text=[metadata['TRCK']]))
        if metadata.get('TCON'): set_frame('TCON', TCON(encoding=3, text=[metadata['TCON']]))
        if metadata.get('TPUB'): set_frame('TPUB', TPUB(encoding=3, text=[metadata['TPUB']]))
        if metadata.get('TSSE'): set_frame('TSSE', TSSE(encoding=3, text=[metadata['TSSE']]))
        if metadata.get('WXXX'):
            id3.delall('WXXX')
            id3.add(WXXX(encoding=3, desc='Author URL', url=metadata['WXXX']))
        if metadata.get('TCOP'): set_frame('TCOP', TCOP(encoding=3, text=[metadata['TCOP']]))
        if metadata.get('TALB'): set_frame('TALB', TALB(encoding=3, text=[metadata['TALB']]))
        for desc in ['Group Description', 'Mood', 'Parental Rating Reason']:
            key = f"TXXX:{desc}"
            if metadata.get(key):
                id3.delall(key)
                id3.add(TXXX(encoding=3, desc=desc, text=[metadata[key]]))
        if metadata.get('TCOM'): set_frame('TCOM', TCOM(encoding=3, text=[metadata['TCOM']]))
        if metadata.get('TPE3'): set_frame('TPE3', TPE3(encoding=3, text=[metadata['TPE3']]))
        # Embed cover art if provided
        cover_bytes, cover_mime = cover
        if cover_bytes and cover_mime:
            id3.delall('APIC')
            id3.add(APIC(encoding=3, mime=cover_mime, type=3, desc='Cover', data=cover_bytes))
        if ext == '.wav':
            # Read audio data
            try:
                with wave.open(file_path, 'rb') as w:
                    params = w.getparams()
                    audio_data = w.readframes(params.nframes)
            except wave.Error as e:
                raise ValueError(f"WAV read failed: {e}")
            # Serialize ID3 to bytes
            f = BytesIO()
            v2_ver = 3 if self.force_v23.get() else 4
            id3.save(f, v2_version=v2_ver)
            tag_data = f.getvalue()
            # Prepare padded chunk
            pad = b'\x00' if len(tag_data) % 2 == 1 else b''
            chunk_id = b'id3 '
            chunk_size_bytes = struct.pack('<I', len(tag_data))
            id3_chunk = chunk_id + chunk_size_bytes + tag_data + pad
            # Write new WAV file
            temp_path = file_path + '.tmp'
            with wave.open(temp_path, 'wb') as w:
                w.setparams(params)
                w.writeframes(audio_data)
            # Append ID3 chunk
            with open(temp_path, 'ab') as f:
                f.write(id3_chunk)
            # Update RIFF size
            with open(temp_path, 'r+b') as f:
                f.seek(4)
                riff_size = struct.unpack('<I', f.read(4))[0]
                new_riff_size = riff_size + len(id3_chunk)
                f.seek(4)
                f.write(struct.pack('<I', new_riff_size))
            os.replace(temp_path, file_path)
        else: # MP3
            try:
                audio = ID3(file_path)
            except MutagenError:
                audio = ID3()
            audio.update(id3)
            v2_ver = 3 if self.force_v23.get() else 4
            audio.save(file_path, v2_version=v2_ver)
        # Optional verification
        if self.verify_writes.get():
            ok, msg = self._verify_file_tags(file_path, metadata)
            if not ok:
                raise ValueError(f"Verify failed: {msg}")
    def _verify_file_tags(self, file_path, expected):
        """Read file and confirm a subset of written tags match expected values."""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.wav':
                tag = WAVE(file_path).tags or ID3()
            else:
                tag = ID3(file_path)
            # Build checks
            def get_text(t, key):
                if key.startswith('TXXX:'):
                    desc = key.split(':',1)[1]
                    for f in t.getall('TXXX'):
                        if getattr(f, 'desc', '') == desc:
                            return (f.text or [''])[0]
                    return ''
                f = t.get(key)
                return (f.text[0] if f and getattr(f, 'text', None) else '')
            checks = ['TPE1','TPE2','TDRC','TRCK','TCON','TPUB','TCOP','TALB','TCOM','TPE3','TXXX:Group Description','TXXX:Mood','TXXX:Parental Rating Reason']
            for k in checks:
                if expected.get(k):
                    got = get_text(tag, k)
                    if str(got).strip() != str(expected[k]).strip():
                        return False, f"{k} → '{got}' != '{expected[k]}'"
            return True, 'ok'
        except Exception as e:
            return False, f"verify exception: {e}"
    def _find_cover_art(self, base_folder):
        candidates = ['cover.jpg', 'cover.jpeg', 'cover.png', 'folder.jpg', 'folder.jpeg', 'folder.png']
        for name in candidates:
            p = os.path.join(base_folder, name)
            if os.path.isfile(p):
                try:
                    with open(p, 'rb') as f:
                        data = f.read()
                    mime = 'image/png' if p.lower().endswith('png') else 'image/jpeg'
                    return (data, mime)
                except Exception:
                    continue
        return (None, None)
    def reset_fields(self):
        for v in self.vars.values():
            v.set("")
    def save_profile(self):
        data = {k: v.get().strip() for k, v in self.vars.items() if v.get().strip()}
        data['__options__'] = {
            'auto_number': self.auto_number.get(),
            'only_fill_missing': self.only_fill_missing.get(),
            'embed_cover': self.embed_cover.get(),
            'verify_writes': self.verify_writes.get(),
            'force_v23': self.force_v23.get(),
            'track_offset': int(self.track_offset.get()),
            'last_folder': getattr(self, 'folder', ''),
            'single_mode': self.single_mode.get(),
            'last_file': self.single_path or ''
        }
        file = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')], title='Save profile as')
        if file:
            try:
                with open(file, 'w') as f:
                    json.dump(data, f, indent=2)
                with open(PROFILE_PATH, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo('Saved', f'Profile saved to {file}')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save profile: {type(e).__name__} - {e}')
    def load_profile(self, path=None, silent=False):
        if not path:
            path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')], title='Load profile')
        if path and os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                options = data.pop('__options__', {})
                for key, value in data.items():
                    if key in self.vars:
                        self.vars[key].set(value)
                self.auto_number.set(bool(options.get('auto_number', self.auto_number.get())))
                self.only_fill_missing.set(bool(options.get('only_fill_missing', self.only_fill_missing.get())))
                self.embed_cover.set(bool(options.get('embed_cover', self.embed_cover.get())))
                self.verify_writes.set(bool(options.get('verify_writes', self.verify_writes.get())))
                self.force_v23.set(bool(options.get('force_v23', self.force_v23.get())))
                self.track_offset.set(int(options.get('track_offset', self.track_offset.get())))
                self.single_mode.set(bool(options.get('single_mode', self.single_mode.get())))
                last_folder = options.get('last_folder')
                if last_folder and os.path.isdir(last_folder):
                    self.folder = last_folder
                    self.dir_label.config(text=last_folder)
                last_file = options.get('last_file')
                if last_file and os.path.isfile(last_file):
                    self.single_path = last_file
                    self.single_file_label.config(text=os.path.basename(last_file))
                if not silent:
                    messagebox.showinfo('Loaded', f'Profile loaded from {path}')
            except Exception as e:
                if not silent:
                    messagebox.showerror('Error', f'Failed to load profile: {type(e).__name__} - {e}')
if __name__ == '__main__':
    MP3TaggerGUI().mainloop()