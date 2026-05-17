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
        on_minimize: callable
    ):
        self.settings_manager = settings_manager
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_minimize = on_minimize
        self.window: tk.Tk = None
        self.is_running = False

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
        self.window.geometry("550x650")
        self.window.resizable(False, False)

        # Установить иконку окна
        try:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"
            if icon_path.exists():
                self.window.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"Could not load window icon: {e}")

        # Перехватываем закрытие окна
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Заголовок
        title_label = tk.Label(
            self.window,
            text="⏸ Time to Pause",
            font=("Arial", 28, "bold"),
            padx=20,
            pady=15
        )
        title_label.pack()

        # Статус
        self.status_label = tk.Label(
            self.window,
            text="Status: Stopped",
            font=("Arial", 12),
            fg="#888888",
            padx=20,
            pady=5
        )
        self.status_label.pack()

        # Separator
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=5)

        # Main content frame
        content_frame = tk.Frame(self.window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Интервал напоминаний
        tk.Label(content_frame, text="Interval between reminders:", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 10))

        self.interval_var = tk.DoubleVar(value=self.settings_manager.config.interval_minutes)
        intervals = [
            (5/60, "⏱ 5 seconds (test)"),
            (30, "⏱ 30 minutes"),
            (60, "⏱ 1 hour"),
            (120, "⏱ 2 hours"),
        ]

        for value, label in intervals:
            rb = tk.Radiobutton(
                content_frame,
                text=label,
                variable=self.interval_var,
                value=value,
                font=("Arial", 10),
                command=self._on_interval_change
            )
            rb.pack(anchor='w', padx=15, pady=4)

        separator2 = ttk.Separator(self.window, orient='horizontal')
        separator2.pack(fill='x', padx=20, pady=10)

        # Тип уведомления
        notification_frame = tk.Frame(self.window)
        notification_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        tk.Label(notification_frame, text="Notification type:", font=("Arial", 11, "bold")).pack(anchor='w', pady=(0, 10))

        self.notification_var = tk.StringVar(value=self.settings_manager.config.notification_type)
        notifications = [
            ("sound", "🔊 Sound only"),
            ("flash", "⚡ Flash only"),
            ("mixed", "🔊⚡ Sound + Flash"),
        ]

        for value, label in notifications:
            rb = tk.Radiobutton(
                notification_frame,
                text=label,
                variable=self.notification_var,
                value=value,
                font=("Arial", 10),
                command=self._on_notification_change
            )
            rb.pack(anchor='w', padx=15, pady=4)

        separator3 = ttk.Separator(self.window, orient='horizontal')
        separator3.pack(fill='x', padx=20, pady=10)

        # Кнопки управления
        button_frame = tk.Frame(self.window, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=20, pady=15)

        self.start_btn = tk.Button(
            button_frame,
            text="▶ START",
            command=self._on_start_click,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 13, "bold"),
            padx=40,
            pady=15,
            width=20,
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
            padx=40,
            pady=15,
            width=20,
            state='disabled',
            cursor="hand2"
        )
        self.stop_btn.pack(side='left', padx=10, pady=10)

        # Footer с инструкцией
        footer_label = tk.Label(
            self.window,
            text="Click ✕ to minimize to system tray",
            font=("Arial", 9),
            fg="#999999",
            padx=20,
            pady=10
        )
        footer_label.pack()

        self.window.mainloop()

    def _on_interval_change(self):
        """Обработчик изменения интервала"""
        interval = self.interval_var.get()
        self.settings_manager.update_interval(interval)

        # Если таймер запущен, перезапустить с новым интервалом
        if self.is_running:
            if self.on_stop:
                self.on_stop()
            if self.on_start:
                self.on_start()

    def _on_notification_change(self):
        """Обработчик изменения типа уведомления"""
        notification_type = self.notification_var.get()
        self.settings_manager.update_notification_type(notification_type)

    def _on_start_click(self):
        """Обработчик кнопки Start"""
        interval = self.interval_var.get()
        notification_type = self.notification_var.get()

        self.settings_manager.update_interval(interval)
        self.settings_manager.update_notification_type(notification_type)

        if self.on_start:
            self.on_start()

        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        interval_display = self._format_interval(interval)
        self.status_label.config(text=f"Status: Running (reminder every {interval_display})", fg="#4CAF50")

    def _on_stop_click(self):
        """Обработчик кнопки Stop"""
        if self.on_stop:
            self.on_stop()

        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="Status: Stopped", fg="#888888")

    def _on_close(self):
        """Обработчик закрытия окна - минимизация в трей"""
        self.window.withdraw()
        if self.on_minimize:
            self.on_minimize()

    def show_window(self):
        """Показать окно из трея"""
        if self.window and self.window.winfo_exists():
            self.window.deiconify()
            self.window.lift()

    def hide_window(self):
        """Скрыть окно в трей"""
        if self.window and self.window.winfo_exists():
            self.window.withdraw()

    def close(self):
        """Закрыть приложение"""
        if self.window and self.window.winfo_exists():
            self.window.destroy()


class SettingsWindow:
    """Окно настроек приложения (для совместимости)"""

    def __init__(self, settings_manager: SettingsManager, on_apply: callable):
        self.settings_manager = settings_manager
        self.on_apply = on_apply
        self.window: tk.Tk = None

    def show(self):
        """Показать окно настроек"""
        if self.window is not None and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Tk()
        self.window.title("Break Reminder - Settings")
        self.window.geometry("400x300")
        self.window.resizable(False, False)

        # Заголовок
        title_label = tk.Label(
            self.window,
            text="⚙ Settings",
            font=("Arial", 16, "bold"),
            padx=20,
            pady=10
        )
        title_label.pack()

        # Separator
        separator = ttk.Separator(self.window, orient='horizontal')
        separator.pack(fill='x', padx=20, pady=5)

        # Frame для элементов
        frame = tk.Frame(self.window, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Интервал напоминаний
        tk.Label(frame, text="Interval between reminders:", font=("Arial", 11)).pack(anchor='w', pady=(0, 10))

        interval_var = tk.DoubleVar(value=self.settings_manager.config.interval_minutes)
        intervals = [
            (5/60, "⏱ 5 seconds (test)"),
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

        # Тип уведомления
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

        # Кнопки
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
        """Сохранить настройки"""
        self.settings_manager.update_interval(interval)
        self.settings_manager.update_notification_type(notification_type)

        if self.on_apply:
            self.on_apply(interval, notification_type)

        self.window.destroy()
