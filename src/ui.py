import tkinter as tk
from tkinter import ttk
from pathlib import Path
from src.settings import SettingsManager

class MainWindow:
    """Главное окно приложения с управлением таймером"""

    def __init__(
        self,
        settings_manager: SettingsManager,
        on_start: callable,
        on_stop: callable,
        on_minimize: callable,
        on_test: callable = None
    ):
        self.settings_manager = settings_manager
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_minimize = on_minimize
        self.on_test = on_test
        self.window: tk.Tk = None
        self.is_running = False
        self.random_mode = False
        self.random_min = 10
        self.random_max = 30
        self.random_notification = False
        self.current_interval = 30.0

    def _format_interval(self, interval: float) -> str:
        """Форматировать интервал для отображения"""
        if interval < 1:
            seconds = int(interval * 60)
            return f"{seconds} sec"
        elif interval == 1:
            return "1 min"
        else:
            return f"{int(interval)} min"

    def show(self):
        """Показать главное окно"""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            self.window.state('normal')
            return

        self.window = tk.Tk()
        self.window.title("Time to Pause")
        self.window.geometry("700x700")
        self.window.resizable(False, False)

        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Could not load window icon: {e}")

        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        title_label = tk.Label(
            self.window,
            text="⏸ Time to Pause",
            font=("Arial", 28, "bold"),
            padx=20,
            pady=15
        )
        title_label.pack()

        self.status_label = tk.Label(
            self.window,
            text="Status: Stopped",
            font=("Arial", 12),
            fg="#888888",
            padx=20,
            pady=5
        )
        self.status_label.pack()

        separator = ttk.Separator(self.window, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=5)

        content_frame = tk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # PRESET BUTTONS
        tk.Label(content_frame, text="Quick presets:", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 10))

        preset_button_frame = tk.Frame(content_frame)
        preset_button_frame.pack(anchor='w', pady=(0, 15), fill='x')

        self.btn_30min = tk.Button(
            preset_button_frame,
            text="30 min",
            command=lambda: self._on_preset_click(30),
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.btn_30min.pack(side='left', padx=5)

        self.btn_1hour = tk.Button(
            preset_button_frame,
            text="1 hour",
            command=lambda: self._on_preset_click(60),
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.btn_1hour.pack(side='left', padx=5)

        self.btn_2hours = tk.Button(
            preset_button_frame,
            text="2 hours",
            command=lambda: self._on_preset_click(120),
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.btn_2hours.pack(side='left', padx=5)

        separator_presets = ttk.Separator(content_frame, orient='horizontal')
        separator_presets.pack(fill='x', pady=10)

        # RANDOM TIME RANGE
        tk.Label(content_frame, text="Random time range (activates automatically):", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 10))

        random_frame = tk.Frame(content_frame)
        random_frame.pack(anchor='w', pady=(0, 15), fill='x')

        tk.Label(random_frame, text="From:", font=("Arial", 10)).pack(side='left', padx=(0, 5))
        self.random_min_var = tk.StringVar(value=str(self.random_min))
        self.random_min_var.trace('w', lambda *args: self._on_random_range_changed())
        random_min_entry = tk.Entry(random_frame, textvariable=self.random_min_var, width=5, font=("Arial", 10))
        random_min_entry.pack(side='left', padx=2)
        tk.Label(random_frame, text="min", font=("Arial", 10)).pack(side='left', padx=(2, 15))

        tk.Label(random_frame, text="To:", font=("Arial", 10)).pack(side='left', padx=(0, 5))
        self.random_max_var = tk.StringVar(value=str(self.random_max))
        self.random_max_var.trace('w', lambda *args: self._on_random_range_changed())
        random_max_entry = tk.Entry(random_frame, textvariable=self.random_max_var, width=5, font=("Arial", 10))
        random_max_entry.pack(side='left', padx=2)
        tk.Label(random_frame, text="min", font=("Arial", 10)).pack(side='left', padx=(2, 15))

        self.random_status_label = tk.Label(
            random_frame,
            text="(not active yet)",
            font=("Arial", 10),
            fg="#999999",
            padx=20
        )
        self.random_status_label.pack(side='left')

        separator_random = ttk.Separator(content_frame, orient='horizontal')
        separator_random.pack(fill='x', pady=10)

        # NOTIFICATION TYPE
        notification_header_frame = tk.Frame(content_frame)
        notification_header_frame.pack(anchor='w', pady=(0, 10), fill='x')

        tk.Label(notification_header_frame, text="Notification type:", font=("Arial", 11, "bold")).pack(side='left', anchor='w')

        self.notification_var = tk.StringVar(value=self.settings_manager.config.notification_type)
        notifications = [
            ("sound", "🔊 Sound only"),
            ("flash", "⚡ Flash only"),
            ("mixed", "🔊⚡ Sound + Flash"),
            ("random", "🎲 Random"),
        ]

        for value, label in notifications:
            rb = tk.Radiobutton(
                content_frame,
                text=label,
                variable=self.notification_var,
                value=value,
                font=("Arial", 10),
                command=self._on_notification_change
            )
            rb.pack(anchor='w', padx=15, pady=4)

        self.notification_status_label = tk.Label(
            content_frame,
            text="",
            font=("Arial", 9),
            fg="#666666",
            padx=15
        )
        self.notification_status_label.pack(anchor='w', pady=(0, 10))
        self._on_notification_changed()

        separator3 = ttk.Separator(self.window, orient='horizontal')
        separator3.pack(fill='x', padx=20, pady=10)

        # CONTROL BUTTONS
        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=15)

        self.start_btn = tk.Button(
            button_frame,
            text="▶ START",
            command=self._on_start_click,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 13, "bold"),
            padx=30,
            pady=15,
            width=12,
            cursor="hand2"
        )
        self.start_btn.pack(side='left', padx=10, pady=10)

        self.stop_btn = tk.Button(
            button_frame,
            text="⏸ STOP",
            command=self._on_stop_click,
            bg="#FF5252",
            fg="white",
            font=("Arial", 13, "bold"),
            padx=30,
            pady=15,
            width=12,
            state='disabled',
            cursor="hand2"
        )
        self.stop_btn.pack(side='left', padx=10, pady=10)

        self.test_btn = tk.Button(
            button_frame,
            text="🧪 TEST\n(3 sec)",
            command=self._on_test_click,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=15,
            pady=10,
            width=10,
            cursor="hand2"
        )
        self.test_btn.pack(side='right', padx=10, pady=10)

        footer_label = tk.Label(
            self.window,
            text="Click X to minimize to system tray",
            font=("Arial", 9),
            fg="#999999",
            padx=20,
            pady=10
        )
        footer_label.pack()

        self.window.mainloop()

    def _on_notification_changed(self):
        """Handle notification type change - update status display"""
        notification_type = self.notification_var.get()
        if notification_type == "random":
            self.notification_status_label.config(
                text="🎲 Will randomly pick: sound, flash, or mixed",
                fg="#666666"
            )
        else:
            icons = {"sound": "🔊", "flash": "⚡", "mixed": "🔊⚡"}
            icon = icons.get(notification_type, "")
            self.notification_status_label.config(
                text=f"{icon} Will use this type",
                fg="#666666"
            )

    def _on_notification_change(self):
        """Handler for notification type change"""
        notification_type = self.notification_var.get()
        if notification_type != "random":
            self.settings_manager.update_notification_type(notification_type)
        self._on_notification_changed()

    def _on_start_click(self):
        """Handle START button click"""
        import random

        try:
            min_val = int(self.random_min_var.get())
            max_val = int(self.random_max_var.get())

            if min_val > 0 and max_val > 0 and min_val <= max_val:
                interval = random.uniform(min_val, max_val)
                interval_display = f"random {min_val}-{max_val} min"
                print(f"🎲 Random interval: {interval:.1f} minutes")
            else:
                interval = self.current_interval
                interval_display = self._format_interval(interval)
        except (ValueError, AttributeError):
            interval = self.current_interval
            interval_display = self._format_interval(interval)

        notification_type = self.notification_var.get()
        if notification_type == "random":
            options = ["sound", "flash", "mixed"]
            notification_type = random.choice(options)
            print(f"🎲 Random notification selected: {notification_type} (from options: {options})")

        self.settings_manager.update_interval(interval)
        self.settings_manager.update_notification_type(notification_type)

        if self.on_start:
            self.on_start()

        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text=f"Status: Running (reminder every {interval_display})", fg="#4CAF50")

    def _on_stop_click(self):
        """Handle STOP button click"""
        if self.on_stop:
            self.on_stop()

        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", fg="#888888")

    def _on_preset_click(self, minutes: int):
        """Handle preset button click"""
        self.current_interval = float(minutes)
        self.settings_manager.update_interval(minutes)
        interval_display = self._format_interval(minutes)

        if self.is_running:
            if self.on_stop:
                self.on_stop()
            if self.on_start:
                self.on_start()

        self.status_label.config(text=f"Status: Ready (interval: {interval_display})", fg="#FF9800")
        self.random_status_label.config(
            text=f"(preset: {interval_display})",
            fg="#666666"
        )
        print(f"📊 Preset selected: {interval_display}")

    def _on_random_range_changed(self):
        """Handle random range value change"""
        try:
            min_val = int(self.random_min_var.get())
            max_val = int(self.random_max_var.get())

            if min_val > 0 and max_val > 0 and min_val <= max_val:
                self.random_mode = True
                self.random_status_label.config(
                    text=f"🎲 Active: {min_val}-{max_val} min",
                    fg="#4CAF50"
                )
                print(f"🎲 Random mode: {min_val}-{max_val} minutes")
            else:
                self.random_mode = False
                self.random_status_label.config(
                    text="(not active yet)",
                    fg="#999999"
                )
        except ValueError:
            self.random_mode = False
            self.random_status_label.config(
                text="(invalid range)",
                fg="#FF5252"
            )
            print("⚠️ Invalid random range values")

    def _on_test_click(self):
        """Handle TEST button click"""
        from tkinter import messagebox
        import threading

        messagebox.showinfo("Test Notification", "Test notification in 3 seconds...\nGet ready!")

        def trigger_test():
            import time
            time.sleep(3)
            if self.on_test:
                self.on_test()

        threading.Thread(target=trigger_test, daemon=True).start()

    def _on_close(self):
        """Handle window close - minimize to tray"""
        self.window.withdraw()
        if self.on_minimize:
            self.on_minimize()

    def show_window(self):
        """Show window from tray"""
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()

    def hide_window(self):
        """Hide window to tray"""
        if self.window and self.window.winfo_exists():
            self.window.withdraw()

    def close(self):
        """Close application"""
        if self.window and self.window.winfo_exists():
            self.window.destroy()


class SettingsWindow:
    """Settings window (for compatibility)"""

    def __init__(self, settings_manager: SettingsManager, on_apply: callable):
        self.settings_manager = settings_manager
        self.on_apply = on_apply
        self.window: tk.Tk = None

    def show(self):
        """Show settings window"""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Tk()
        self.window.title("Break Reminder - Settings")
        self.window.geometry("400x300")
        self.window.resizable(False, False)

        title_label = tk.Label(
            self.window,
            text="⚙ Settings",
            font=("Arial", 16, "bold"),
            padx=20,
            pady=10
        )
        title_label.pack()

        separator = ttk.Separator(self.window, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=5)

        frame = tk.Frame(self.window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Interval between reminders:", font=("Arial", 11)).pack(anchor='w', pady=(0, 10))

        interval_var = tk.DoubleVar(value=self.settings_manager.config.interval_minutes)
        intervals = [
            (3/60, "⏱ 3 seconds (test)"),
            (30, "⏱ 30 minutes"),
            (60, "⏱ 1 hour"),
            (120, "⏱ 2 hours"),
        ]

        for value, label in intervals:
            rb = tk.Radiobutton(
                frame,
                text=label,
                variable=interval_var,
                value=value,
                font=("Arial", 10)
            )
            rb.pack(anchor='w', padx=20, pady=5)

        separator2 = ttk.Separator(self.window, orient='horizontal')
        separator2.pack(fill='x', padx=20, pady=10)

        tk.Label(frame, text="Notification type:", font=("Arial", 11)).pack(anchor='w', pady=(0, 10))

        notification_var = tk.StringVar(value=self.settings_manager.config.notification_type)
        notifications = [
            ("sound", "Sound only 🔊"),
            ("flash", "Flash only ⚡"),
            ("mixed", "Sound + Flash 🔊⚡"),
        ]

        for value, label in notifications:
            rb = tk.Radiobutton(
                frame,
                text=label,
                variable=notification_var,
                value=value,
                font=("Arial", 10)
            )
            rb.pack(anchor='w', padx=20, pady=5)

        button_frame = tk.Frame(self.window, padx=20, pady=20)
        button_frame.pack(fill='x')

        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=lambda: self._on_save(interval_var.get(), notification_var.get()),
            bg="#00D4FF",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        )
        save_btn.pack(side='left', padx=5)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy,
            bg="#888888",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        )
        cancel_btn.pack(side='left', padx=5)

        self.window.mainloop()

    def _on_save(self, interval: int, notification_type: str):
        """Save settings"""
        self.settings_manager.update_interval(interval)
        self.settings_manager.update_notification_type(notification_type)

        if self.on_apply:
            self.on_apply(interval, notification_type)

        self.window.destroy()
