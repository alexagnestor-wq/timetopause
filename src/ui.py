import tkinter as tk
from pathlib import Path
from src.settings import SettingsManager

_BG = '#ffffff'
_FG = '#000000'
_BORDER = '#000000'
_HOVER = '#f0f0f0'
_ACTIVE_HOVER = '#333333'
_DISABLED_BG = '#cccccc'
_DISABLED_FG = '#888888'


class PixelButton(tk.Canvas):
    """Pixel-art button: 4 black border strips with corner gaps (CSS box-shadow style)."""

    BW = 3  # border strip width

    def __init__(self, parent, text='', command=None,
                 font=None, bg=_BG, fg=_FG,
                 height=38, state='normal', cursor='hand2',
                 image=None, image_active=None, **_):
        super().__init__(
            parent, bd=0, highlightthickness=0,
            bg=parent['bg'], height=height + 2 * self.BW, cursor=cursor
        )
        self._text = text
        self._command = command
        self._font = font or ('Arial', 9, 'bold')
        self._bg = bg
        self._fg = fg
        self._disabled = (state == 'disabled')
        self._hover = False
        self._pressed = False
        self._image = image
        self._image_active = image_active

        self.bind('<Configure>', self._draw)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)
        self.bind('<Enter>', lambda e: self._set_hover(True))
        self.bind('<Leave>', lambda e: self._set_hover(False))

    def _eff_bg(self):
        if self._disabled:
            return _DISABLED_BG
        if self._hover and not self._pressed:
            return _ACTIVE_HOVER if self._bg == _FG else _HOVER
        return self._bg

    def _eff_fg(self):
        return _DISABLED_FG if self._disabled else self._fg

    def _draw(self, event=None):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 1 or h <= 1:
            return

        BW = self.BW
        bg, fg = self._eff_bg(), self._eff_fg()
        press = 2 if self._pressed else 0

        # Drop shadow (bottom + right, grey ≈ css #00000038 on white)
        if not self._pressed:
            self.create_rectangle(BW, h - BW + 2, w - BW, h,      fill='#b0b0b0', outline='')
            self.create_rectangle(w - BW + 2, BW, w, h - BW + 2,  fill='#b0b0b0', outline='')

        # Four black border strips — corners stay canvas-bg (pixel gap effect)
        self.create_rectangle(BW,     0,      w - BW, BW,     fill='#000000', outline='')  # top
        self.create_rectangle(BW,     h - BW, w - BW, h,      fill='#000000', outline='')  # bottom
        self.create_rectangle(0,      BW,     BW,     h - BW, fill='#000000', outline='')  # left
        self.create_rectangle(w - BW, BW,     w,      h - BW, fill='#000000', outline='')  # right

        # Button body
        self.create_rectangle(BW, BW, w - BW, h - BW, fill=bg, outline='')

        # Icon + text, or just text
        # Use inverted (white) icon when button has dark/active background
        use_image = self._image
        if self._image_active and self._bg == _FG:
            use_image = self._image_active

        if use_image:
            iw = use_image.width()
            pad = 8
            icon_x = BW + pad + iw // 2
            self.create_image(icon_x, h // 2 + press, image=use_image, anchor='center')
            text_left = BW + pad + iw + pad
            text_x = text_left + (w - BW - text_left) // 2
            self.create_text(text_x, h // 2 + press, text=self._text, fill=fg, font=self._font, anchor='center')
        else:
            self.create_text(w // 2, h // 2 + press, text=self._text, fill=fg, font=self._font)

    def config(self, **kw):
        for k in ('activebackground', 'activeforeground', 'relief', 'bd', 'padx', 'pady'):
            kw.pop(k, None)
        redraw = False
        for attr, key in (('_bg', 'bg'), ('_fg', 'fg'), ('_text', 'text'), ('_image', 'image'), ('_image_active', 'image_active')):
            if key in kw:
                setattr(self, attr, kw.pop(key))
                redraw = True
        if 'state' in kw:
            self._disabled = kw.pop('state') == 'disabled'
            redraw = True
        if kw:
            super().config(**kw)
        if redraw:
            self._draw()

    configure = config

    def _on_press(self, event):
        if not self._disabled:
            self._pressed = True
            self._draw()

    def _on_release(self, event):
        if self._pressed:
            self._pressed = False
            self._draw()
            if self._command:
                self._command()

    def _set_hover(self, val):
        self._hover = val
        self._draw()


class PixelSlider(tk.Canvas):
    """Pixel-art horizontal slider: thick black track + white square thumb."""

    THUMB_W  = 20
    THUMB_H  = 20
    TRACK_H  = 6
    BW       = 3   # thumb border strip width
    PAD      = 12  # horizontal padding so thumb stays inside

    def __init__(self, parent, from_=0, to=100, variable=None, **kw):
        super().__init__(
            parent, bd=0, highlightthickness=0,
            bg=parent['bg'], height=self.THUMB_H + 10,
        )
        self._from = from_
        self._to   = to
        self._var  = variable if variable is not None else tk.IntVar(value=from_)

        self.bind('<Configure>',  self._draw)
        self.bind('<Button-1>',   self._on_click)
        self.bind('<B1-Motion>',  self._on_drag)
        self._var.trace_add('write', lambda *_: self._draw())

    def _val_to_x(self, val, w):
        ratio = (val - self._from) / max(1, self._to - self._from)
        return self.PAD + ratio * (w - 2 * self.PAD)

    def _x_to_val(self, x, w):
        ratio = (x - self.PAD) / max(1, w - 2 * self.PAD)
        return int(round(self._from + max(0.0, min(1.0, ratio)) * (self._to - self._from)))

    def _draw(self, event=None):
        self.delete('all')
        w, h = self.winfo_width(), self.winfo_height()
        if w <= 1:
            return

        val = self._var.get()
        cx  = self._val_to_x(val, w)
        cy  = h // 2

        # Track
        self.create_rectangle(
            self.PAD, cy - self.TRACK_H // 2,
            w - self.PAD, cy + self.TRACK_H // 2,
            fill='#000000', outline=''
        )

        # Thumb — pixel border (corner gaps) + white body
        BW = self.BW
        tx1, ty1 = int(cx) - self.THUMB_W // 2, cy - self.THUMB_H // 2
        tx2, ty2 = tx1 + self.THUMB_W,           ty1 + self.THUMB_H

        self.create_rectangle(tx1+BW, ty1,    tx2-BW, ty1+BW, fill='#000000', outline='')  # top
        self.create_rectangle(tx1+BW, ty2-BW, tx2-BW, ty2,    fill='#000000', outline='')  # bottom
        self.create_rectangle(tx1,    ty1+BW, tx1+BW, ty2-BW, fill='#000000', outline='')  # left
        self.create_rectangle(tx2-BW, ty1+BW, tx2,    ty2-BW, fill='#000000', outline='')  # right
        self.create_rectangle(tx1+BW, ty1+BW, tx2-BW, ty2-BW, fill='#ffffff', outline='')  # body

    def _on_click(self, event):
        self._var.set(self._x_to_val(event.x, self.winfo_width()))

    def _on_drag(self, event):
        self._var.set(self._x_to_val(event.x, self.winfo_width()))


class MainWindow:
    def __init__(
        self,
        settings_manager: SettingsManager,
        on_start: callable,
        on_stop: callable,
        on_minimize: callable,
        on_test: callable = None,
        on_settings: callable = None,
        on_rainbow_test: callable = None,
        on_exit: callable = None,
        on_calendar: callable = None,
    ):
        self.settings_manager = settings_manager
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_minimize = on_minimize
        self.on_test = on_test
        self.on_settings = on_settings
        self.on_rainbow_test = on_rainbow_test
        self.on_exit = on_exit
        self.on_calendar = on_calendar
        self._calendar_btn = None

        self.window: tk.Tk = None
        self.is_running = False
        self.current_interval = 30.0

        # Public refs accessed by main.py
        self.start_btn: tk.Button = None
        self.stop_btn: tk.Button = None
        self.status_label: tk.Label = None
        self.notification_var: tk.StringVar = None

        self._interval_btns: dict = {}
        self._notif_btns: dict = {}
        self._status_subtext: tk.Label = None
        self._icons: dict = {}

    def show(self, on_window_created: callable = None):
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.state('normal')
            return

        self.window = tk.Tk()

        if on_window_created:
            on_window_created(self.window)

        self._load_icons()

        self.window.title("Time to Pause")
        self.window.geometry("400x800")
        self.window.resizable(False, False)
        self.window.configure(bg=_BG)

        try:
            icon_path = Path(__file__).parent.parent / "assets" / "app_icon2.ico"
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception:
            pass

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        main = tk.Frame(self.window, bg=_BG, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        self._build_header(main)
        self._build_status_card(main)
        self._build_interval_section(main)
        self._build_notification_section(main)
        self._build_action_buttons(main)
        self._build_secondary_buttons(main)

        self.window.mainloop()

    def _load_icons(self):
        icons_dir = Path(__file__).parent.parent / "assets" / "icons"
        try:
            from PIL import Image, ImageOps, ImageTk
            for name in ("sound", "flash", "mixed", "random", "play"):
                path = icons_dir / f"{name}.png"
                if not path.exists():
                    continue
                img = Image.open(str(path)).convert("RGBA")
                self._icons[name] = ImageTk.PhotoImage(img)

                # Inverted version: flip RGB channels, keep alpha → white icon for dark bg
                r, g, b, a = img.split()
                inv_rgb = ImageOps.invert(Image.merge("RGB", (r, g, b)))
                inv_img = Image.merge("RGBA", (*inv_rgb.split(), a))
                self._icons[f"{name}_inv"] = ImageTk.PhotoImage(inv_img)
        except Exception as e:
            print(f"Icon load error: {e}")

    # ------------------------------------------------------------------
    # Layout builders
    # ------------------------------------------------------------------

    def _build_header(self, parent):
        frame = tk.Frame(parent, bg=_BG)
        frame.pack(fill='x', pady=(0, 8))

        # Icon box (transparent / white background)
        icon_box = tk.Frame(frame, bg=_BG, width=120, height=120)
        icon_box.pack(side='left', padx=(0, 15))
        icon_box.pack_propagate(False)

        try:
            from PIL import Image, ImageTk
            icon_path = Path(__file__).parent.parent / "assets" / "app_icon2.ico"
            if icon_path.exists():
                img = Image.open(str(icon_path)).resize((112, 112), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(icon_box, image=photo, bg=_BG, bd=0)
                lbl.image = photo
                lbl.place(relx=0.5, rely=0.5, anchor='center')
        except Exception:
            tk.Label(icon_box, text="⏸", font=('Arial', 22), bg=_BG, fg=_FG).place(
                relx=0.5, rely=0.5, anchor='center'
            )

        # Title
        title_frame = tk.Frame(frame, bg=_BG)
        title_frame.pack(side='left', fill='y')

        tk.Label(
            title_frame,
            text="TIME\nTO PAUSE",
            font=('Karmatic Arcade', 22),
            bg=_BG, fg=_FG, anchor='w', justify='left'
        ).pack(anchor='w')

        tk.Label(
            title_frame,
            text="STAY HEALTHY",
            font=('Arial', 9, 'bold'),
            bg=_BG, fg=_FG, anchor='w'
        ).pack(anchor='w')

    def _build_status_card(self, parent):
        card = tk.Frame(
            parent, bg=_BG,
            highlightbackground=_BORDER,
            highlightthickness=3
        )
        card.pack(fill='x', pady=(0, 8))

        inner = tk.Frame(card, bg=_BG, padx=15, pady=12)
        inner.pack(fill='x')

        # Indicator square — top right
        indicator = tk.Frame(inner, bg=_FG, width=16, height=16)
        indicator.pack(side='right', anchor='n', pady=2)
        indicator.pack_propagate(False)

        tk.Label(inner, text="STATUS", font=('Arial', 8, 'bold'), bg=_BG, fg=_FG, anchor='w').pack(anchor='w')

        self.status_label = tk.Label(
            inner,
            text="STOPPED",
            font=('Arial Black', 16, 'bold'),
            bg=_BG, fg=_FG, anchor='w'
        )
        self.status_label.pack(anchor='w')

        self._status_subtext = tk.Label(
            inner,
            text="",
            font=('Arial', 9),
            bg=_BG, fg=_FG, anchor='w'
        )
        self._status_subtext.pack(anchor='w')

    def _build_interval_section(self, parent):
        tk.Label(
            parent, text="INTERVAL",
            font=('Arial', 8, 'bold'),
            bg=_BG, fg=_FG, anchor='w'
        ).pack(anchor='w', pady=(0, 8))

        frame = tk.Frame(parent, bg=_BG)
        frame.pack(fill='x', pady=(0, 8))

        presets = [(30, "30 MIN"), (60, "1 HOUR"), ("custom", "CUSTOM")]

        for i, (key, label) in enumerate(presets):
            if key == "custom":
                active = self.current_interval not in (30.0, 60.0)
            else:
                active = (key == int(self.current_interval))
            btn = PixelButton(
                frame,
                text=label,
                command=lambda k=key: self._on_preset_click(k),
                font=('Arial', 9, 'bold'),
                bg=_FG if active else _BG,
                fg=_BG if active else _FG,
                height=38,
            )
            if i == 0:
                padx = (0, 4)
            elif i == 1:
                padx = (4, 4)
            else:
                padx = (4, 0)
            btn.grid(row=0, column=i, sticky='ew', padx=padx)
            self._interval_btns[key] = btn

        for i in range(3):
            frame.columnconfigure(i, weight=1)

    def _build_notification_section(self, parent):
        tk.Label(
            parent, text="NOTIFICATION",
            font=('Arial', 8, 'bold'),
            bg=_BG, fg=_FG, anchor='w'
        ).pack(anchor='w', pady=(0, 8))

        self.notification_var = tk.StringVar(value=self.settings_manager.config.notification_type)

        frame = tk.Frame(parent, bg=_BG)
        frame.pack(fill='x', pady=(0, 8))

        notifs = [
            ("sound", "SOUND"),
            ("flash", "FLASH"),
            ("mixed", "MIXED"),
            ("random", "RANDOM"),
        ]
        current = ""  # start with all buttons unselected (white)

        for i, (value, label) in enumerate(notifs):
            row, col = divmod(i, 2)
            active = (value == current)
            btn = PixelButton(
                frame,
                text=label,
                image=self._icons.get(value),
                image_active=self._icons.get(f"{value}_inv"),
                command=lambda v=value: self._on_notification_click(v),
                font=('Arial', 9, 'bold'),
                bg=_FG if active else _BG,
                fg=_BG if active else _FG,
                height=38,
            )
            btn.grid(
                row=row, column=col, sticky='ew',
                padx=(0, 4) if col == 0 else (4, 0),
                pady=(0, 4) if row == 0 else (4, 0)
            )
            self._notif_btns[value] = btn

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def _build_action_buttons(self, parent):
        frame = tk.Frame(parent, bg=_BG)
        frame.pack(fill='x', pady=(0, 8))

        self.start_btn = PixelButton(
            frame,
            text="▶ START",
            command=self._on_start_click,
            font=('Arial', 11, 'bold'),
            bg=_FG, fg=_BG,
            height=44,
        )
        self.start_btn.grid(row=0, column=0, sticky='ew', padx=(0, 4))

        self.stop_btn = PixelButton(
            frame,
            text="⏸ STOP",
            command=self._on_stop_click,
            font=('Arial', 11, 'bold'),
            bg=_BG, fg=_FG,
            height=44,
            state='disabled',
        )
        self.stop_btn.grid(row=0, column=1, sticky='ew', padx=(4, 0))

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def _build_secondary_buttons(self, parent):
        PixelButton(
            parent,
            text="⭐ TEST NOTIFICATION",
            command=self._on_test_click,
            font=('Arial', 9, 'bold'),
            bg=_BG, fg=_FG,
            height=38,
        ).pack(fill='x', pady=(0, 8))

        self._calendar_btn = PixelButton(
            parent,
            text="📅 CONNECT CALENDAR",
            command=self._on_calendar_click,
            font=('Arial', 9, 'bold'),
            bg=_BG, fg=_FG,
            height=38,
        )
        self._calendar_btn.pack(fill='x', pady=(0, 8))

        PixelButton(
            parent,
            text="⚙ SETTINGS",
            command=self._on_settings_click,
            font=('Arial', 9, 'bold'),
            bg=_BG, fg=_FG,
            height=38,
        ).pack(fill='x', pady=(0, 8))

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def _set_running_visual(self):
        interval_label = self._format_interval(self.current_interval)
        self.status_label.config(text="RUNNING")
        self._status_subtext.config(text=f"EVERY {interval_label}")
        self.start_btn.config(state='disabled', bg=_DISABLED_BG, fg=_DISABLED_FG)
        self.stop_btn.config(
            state='normal',
            bg=_FG, fg=_BG,
            activebackground=_ACTIVE_HOVER, activeforeground=_BG,
        )

    def _set_stopped_visual(self):
        self.status_label.config(text="STOPPED")
        self._status_subtext.config(text="")
        self.start_btn.config(
            state='normal',
            bg=_FG, fg=_BG,
            activebackground=_ACTIVE_HOVER, activeforeground=_BG,
        )
        self.stop_btn.config(state='disabled', bg=_BG, fg=_FG)

    def set_stopped_state(self):
        """Called from main.py to reset UI after auto-stop."""
        self.is_running = False
        self._set_stopped_visual()

    def _select_interval_btn(self, key):
        for k, btn in self._interval_btns.items():
            if k == key:
                btn.config(bg=_FG, fg=_BG, activebackground=_ACTIVE_HOVER, activeforeground=_BG)
            else:
                btn.config(bg=_BG, fg=_FG, activebackground=_HOVER, activeforeground=_FG)

    def _select_notif_btn(self, value: str):
        for v, btn in self._notif_btns.items():
            if v == value:
                btn.config(bg=_FG, fg=_BG, activebackground=_ACTIVE_HOVER, activeforeground=_BG)
            else:
                btn.config(bg=_BG, fg=_FG, activebackground=_HOVER, activeforeground=_FG)

    def _format_interval(self, interval: float) -> str:
        if interval < 1:
            return f"{int(interval * 60)} SEC"
        elif interval == 1:
            return "1 MIN"
        return f"{int(interval)} MIN"

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_preset_click(self, key):
        if key == "custom":
            self._show_custom_interval_dialog()
            return
        minutes = int(key)
        self.current_interval = float(minutes)
        self.settings_manager.update_interval(minutes)
        self._select_interval_btn(key)

        if self.is_running:
            if self.on_stop:
                self.on_stop()
            if self.on_start:
                self.on_start()

        if self.is_running:
            self._status_subtext.config(text=f"EVERY {self._format_interval(minutes)}")

    def _show_custom_interval_dialog(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("")
        dialog.geometry("260x210")
        dialog.resizable(False, False)
        dialog.configure(bg=_BG)
        dialog.attributes('-topmost', True)
        dialog.grab_set()

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 260) // 2
        y = (dialog.winfo_screenheight() - 210) // 2
        dialog.geometry(f"260x210+{x}+{y}")

        main = tk.Frame(dialog, bg=_BG, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main, text="CHOOSE TIME\nINTERVAL",
            font=('Karmatic Arcade', 14),
            bg=_BG, fg=_FG, justify='center', anchor='center'
        ).pack(anchor='center', pady=(0, 12))

        # Pixel-border entry
        border = tk.Frame(main, bg=_FG, padx=3, pady=3)
        border.pack(fill='x', pady=(0, 4))

        var = tk.StringVar(value=str(int(self.current_interval)))
        entry = tk.Entry(
            border, textvariable=var,
            font=('Arial', 14, 'bold'),
            bg=_BG, fg=_FG, bd=0,
            insertbackground=_FG, justify='center'
        )
        entry.pack(fill='x', ipady=6)

        tk.Label(
            main, text="MINUTES",
            font=('Arial', 8, 'bold'),
            bg=_BG, fg='#888888'
        ).pack(anchor='center', pady=(0, 12))

        def on_set():
            try:
                val = float(var.get().replace(',', '.'))
                if val > 0:
                    self.current_interval = val
                    self.settings_manager.update_interval(val)
                    self._select_interval_btn("custom")
                    if self.is_running:
                        self._status_subtext.config(text=f"EVERY {self._format_interval(val)}")
                    dialog.destroy()
            except ValueError:
                pass

        PixelButton(
            main, text="SET",
            command=on_set,
            font=('Arial', 11, 'bold'),
            bg=_FG, fg=_BG, height=48
        ).pack(fill='x')

        entry.focus_set()
        entry.select_range(0, 'end')
        dialog.bind('<Return>', lambda e: on_set())

    def _on_notification_click(self, value: str):
        self.notification_var.set(value)
        self._select_notif_btn(value)
        if value != "random":
            self.settings_manager.update_notification_type(value)

    def _on_start_click(self):
        import random

        notification_type = self.notification_var.get()
        if notification_type == "random":
            notification_type = random.choice(["sound", "flash", "mixed"])

        self.settings_manager.update_interval(self.current_interval)
        self.settings_manager.update_notification_type(notification_type)

        if self.on_start:
            self.on_start()

        self.is_running = True
        self._set_running_visual()

    def _on_stop_click(self):
        if self.on_stop:
            self.on_stop()

        self.is_running = False
        self._set_stopped_visual()

    def _on_test_click(self):
        from tkinter import messagebox
        import threading, time

        messagebox.showinfo("Test Notification", "Test notification in 3 seconds...\nGet ready!")

        def trigger():
            time.sleep(3)
            if self.on_test:
                self.on_test()

        threading.Thread(target=trigger, daemon=True).start()

    def _on_rainbow_test_click(self):
        if self.on_rainbow_test:
            self.on_rainbow_test()

    def _on_calendar_click(self):
        if self.on_calendar:
            self.on_calendar()

    def set_calendar_connected(self, connected: bool):
        """Update calendar button appearance (call from main thread)."""
        if self._calendar_btn:
            if connected:
                self._calendar_btn.config(text="📅 DISCONNECT CALENDAR", bg=_FG, fg=_BG)
            else:
                self._calendar_btn.config(text="📅 CONNECT CALENDAR", bg=_BG, fg=_FG)

    def _on_settings_click(self):
        if self.on_settings:
            self.on_settings()

    def _on_close(self):
        if self.settings_manager.config.keep_in_tray:
            self.window.withdraw()
            if self.on_minimize:
                self.on_minimize()
        else:
            if self.on_exit:
                self.on_exit()

    # ------------------------------------------------------------------
    # Public window control
    # ------------------------------------------------------------------

    def show_window(self):
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()

    def hide_window(self):
        if self.window and self.window.winfo_exists():
            self.window.withdraw()

    def close(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()


class SettingsWindow:
    """Settings window"""

    def __init__(self, settings_manager: SettingsManager, main_window, on_apply: callable):
        self.settings_manager = settings_manager
        self.main_window = main_window
        self.on_apply = on_apply
        self.window = None

    def show(self):
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return

        parent = self.main_window.window
        if not parent or not parent.winfo_exists():
            return

        self.window = tk.Toplevel(parent)
        self.window.title("")
        self.window.geometry("300x370")
        self.window.resizable(False, False)
        self.window.configure(bg=_BG)
        self.window.attributes('-topmost', True)
        self.window.grab_set()

        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 300) // 2
        y = (self.window.winfo_screenheight() - 370) // 2
        self.window.geometry(f"300x370+{x}+{y}")

        main = tk.Frame(self.window, bg=_BG, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            main, text="SETTINGS",
            font=('Karmatic Arcade', 16),
            bg=_BG, fg=_FG
        ).pack(pady=(0, 16))

        # Volume
        tk.Label(
            main, text="VOLUME",
            font=('Arial', 8, 'bold'),
            bg=_BG, fg=_FG, anchor='w'
        ).pack(anchor='w')

        volume_var = tk.IntVar(value=self.settings_manager.config.volume)
        PixelSlider(
            main, from_=0, to=100, variable=volume_var,
        ).pack(fill='x', pady=(4, 4))

        tk.Label(
            main, textvariable=volume_var,
            font=('Arial', 8, 'bold'),
            bg=_BG, fg=_FG
        ).pack(anchor='w', pady=(0, 12))

        # Divider
        tk.Frame(main, bg=_FG, height=2).pack(fill='x', pady=(0, 12))

        # Keep in tray
        keep_var = tk.BooleanVar(value=self.settings_manager.config.keep_in_tray)
        tk.Checkbutton(
            main,
            text="Keep in tray when close",
            variable=keep_var,
            font=('Arial', 10),
            bg=_BG, fg=_FG,
            activebackground=_BG, activeforeground=_FG,
            selectcolor=_BG,
            anchor='w'
        ).pack(anchor='w', pady=(0, 16))

        # Divider
        tk.Frame(main, bg=_FG, height=2).pack(fill='x', pady=(0, 12))

        # Calendar alert minutes
        tk.Label(
            main, text="ALERT BEFORE CALL",
            font=('Arial', 8, 'bold'),
            bg=_BG, fg=_FG, anchor='w'
        ).pack(anchor='w')

        cal_frame = tk.Frame(main, bg=_BG)
        cal_frame.pack(fill='x', pady=(4, 12))

        cal_border = tk.Frame(cal_frame, bg=_FG, padx=2, pady=2)
        cal_border.pack(side='left')
        cal_var = tk.StringVar(value=str(self.settings_manager.config.calendar_alert_minutes))
        cal_entry = tk.Entry(
            cal_border, textvariable=cal_var,
            font=('Arial', 12, 'bold'),
            bg=_BG, fg=_FG, bd=0,
            insertbackground=_FG, justify='center', width=4
        )
        cal_entry.pack(ipady=4)

        tk.Label(
            cal_frame, text="  minutes before",
            font=('Arial', 9), bg=_BG, fg='#888888'
        ).pack(side='left', anchor='w')

        def on_save():
            self.settings_manager.config.volume = volume_var.get()
            self.settings_manager.config.keep_in_tray = keep_var.get()
            try:
                mins = int(cal_var.get())
                if mins > 0:
                    self.settings_manager.config.calendar_alert_minutes = mins
            except ValueError:
                pass
            self.settings_manager.save_config()
            if self.on_apply:
                self.on_apply(volume_var.get(), keep_var.get(),
                              self.settings_manager.config.calendar_alert_minutes)
            self.window.destroy()

        PixelButton(
            main, text="SAVE",
            command=on_save,
            font=('Arial', 11, 'bold'),
            bg=_FG, fg=_BG, height=44
        ).pack(fill='x')

        self.window.mainloop()

