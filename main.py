#!/usr/bin/env python3
"""
Break Reminder - Windows Desktop App
Напоминает пользователю сделать паузу в работе
"""

import sys
import time
import ctypes
from pathlib import Path

# Добавим текущую папку в path для импортов
sys.path.insert(0, str(Path(__file__).parent))


def _load_bundled_fonts():
    """Load custom fonts from assets/fonts/ at runtime (no system install needed)."""
    try:
        fonts_dir = Path(__file__).parent / 'assets' / 'fonts'
        if not fonts_dir.exists():
            return
        FR_PRIVATE = 0x10
        for font_file in fonts_dir.glob('*.ttf'):
            ctypes.windll.gdi32.AddFontResourceExW(str(font_file), FR_PRIVATE, 0)
            print(f"[FONT] Loaded: {font_file.name}")
    except Exception as e:
        print(f"[FONT] Could not load fonts: {e}")


_load_bundled_fonts()

from src.settings import SettingsManager
from src.timer import ReminderTimer
from src.notifications import NotificationManager
from src.tray_manager import TrayManager
from src.ui import MainWindow, SettingsWindow
from src.updater import UpdateChecker
from src.calendar_manager import CalendarManager
from src.version import APP_VERSION


class BreakReminderApp:
    """Основное приложение Break Reminder"""

    def __init__(self):
        self.settings_manager = SettingsManager()
        self.notification_manager = NotificationManager(self.settings_manager.assets_dir)
        self.timer = ReminderTimer(
            callback=self._on_reminder,
            interval_minutes=self.settings_manager.config.interval_minutes
        )
        self.tray_manager = TrayManager(
            on_start=self._on_app_start,
            on_stop=self._on_app_stop,
            on_show=self._on_show_window,
            on_exit=self._on_exit
        )
        self.calendar_manager = CalendarManager(
            data_dir=self.settings_manager.config_dir,
            lead_minutes=self.settings_manager.config.calendar_alert_minutes,
            on_event=self._on_calendar_event,
            on_status_change=self._on_calendar_status,
        )
        self.main_window = MainWindow(
            self.settings_manager,
            on_start=self._on_timer_start,
            on_stop=self._on_timer_stop,
            on_minimize=self._on_window_minimize,
            on_test=self._on_test_notification,
            on_settings=self._on_settings,
            on_rainbow_test=self._on_rainbow_test,
            on_exit=self._on_exit,
            on_calendar=self._on_calendar_connect,
        )
        self.settings_window = SettingsWindow(
            self.settings_manager,
            main_window=self.main_window,
            on_apply=self._on_settings_apply
        )
        self.update_checker = UpdateChecker(on_update_available=self._on_update_available)
        self.update_version = None

    def run(self):
        """Запустить приложение"""
        print("=" * 50)
        print("[APP] Time to Pause Started (v{})".format(APP_VERSION))
        print("=" * 50)
        print("[OK] Click START button to begin")

        # Check for updates in background
        print("[UPDATE] Checking for updates...")
        self.update_checker.check_for_updates()

        # Resume calendar polling if already authenticated
        if self.calendar_manager.is_authenticated():
            print("[CALENDAR] Resuming calendar sync...")
            self.calendar_manager.start_polling()

        self.tray_manager.start()
        self.main_window.show(on_window_created=self._on_main_window_created)

        # Главное окно уже блокирует поток

    def _on_main_window_created(self, root):
        self.notification_manager.set_root_window(root)
        if self.calendar_manager.is_authenticated():
            self.main_window.set_calendar_connected(True)

    def _on_timer_start(self):
        """Обработчик запуска таймера"""
        # Обновляем интервал таймера перед запуском (пользователь мог выбрать новый интервал)
        self.timer.update_interval(self.settings_manager.config.interval_minutes)
        print("[OK] Timer started")
        self.timer.start()
        self.tray_manager.show_notification(
            "Break Reminder",
            "Reminder started! Interval: {} minutes".format(
                self.settings_manager.config.interval_minutes
            )
        )

    def _on_timer_stop(self):
        """Обработчик остановки таймера"""
        print("[STOP] Timer stopped")
        self.timer.stop()
        self.tray_manager.show_notification(
            "Break Reminder",
            "Reminder stopped."
        )

    def _on_app_start(self):
        """Обработчик запуска приложения (из трея)"""
        self._on_timer_start()

    def _on_app_stop(self):
        """Обработчик остановки приложения (из трея)"""
        self._on_timer_stop()

    def _on_window_minimize(self):
        """Обработчик минимизации окна в трей"""
        print("[TRAY] Window minimized to tray")
        self.tray_manager.show_notification(
            "Break Reminder",
            "Running in background..."
        )

    def _on_show_window(self):
        """Обработчик показа окна из трея"""
        print("[TRAY] Window restored from tray")
        self.main_window.show_window()

    def _on_reminder(self):
        """Обработчик напоминания (вызывается таймером)"""
        config = self.settings_manager.config
        print(f"\n🔔 REMINDER! ({time.strftime('%H:%M:%S')})")

        # Callback для кнопки STOP в notification окне
        def on_notification_stop():
            print("⏹️ User stopped from notification")
            self._on_timer_stop()
            if self.main_window.window and self.main_window.window.winfo_exists():
                self.main_window.window.after(0, self._update_ui_after_reminder)

        self.notification_manager.notify(
            notification_type=config.notification_type,
            volume=config.volume,
            on_stop=on_notification_stop
        )

        self.tray_manager.show_notification(
            "Break Reminder",
            "Time to take a break! 💪"
        )

        # Auto-stop timer after notification completes (with delay for visual effects)
        # Flash and sound take ~3 seconds, so wait that long before stopping
        print("[AUTO-STOP] Auto-stopping timer in 3.5 seconds (after notification effects)")
        import threading
        def auto_stop_timer():
            time.sleep(3.5)
            self._on_timer_stop()
            if self.main_window.window and self.main_window.window.winfo_exists():
                self.main_window.window.after(0, self._update_ui_after_reminder)

        threading.Thread(target=auto_stop_timer, daemon=True).start()

    def _update_ui_after_reminder(self):
        """Update UI on main thread after reminder"""
        self.main_window.set_stopped_state()

    def _on_settings(self):
        """Обработчик открытия окна настроек"""
        print("⚙ Opening settings...")
        self.settings_window.show()

    def _on_settings_apply(self, volume: int, keep_in_tray: bool, calendar_alert_minutes: int = 10):
        """Обработчик применения новых настроек"""
        print(f"✓ Settings applied: volume={volume}, keep_in_tray={keep_in_tray}, cal_alert={calendar_alert_minutes}")
        self.calendar_manager.update_lead_minutes(calendar_alert_minutes)

    def _on_calendar_connect(self):
        """User clicked Connect Calendar button."""
        if not self.calendar_manager.has_credentials():
            if self.main_window.window:
                from tkinter import messagebox
                self.main_window.window.after(0, lambda: messagebox.showinfo(
                    "Google Calendar Setup",
                    "To connect Google Calendar:\n\n"
                    "1. Go to console.cloud.google.com\n"
                    "2. Create a project & enable Calendar API\n"
                    "3. Create OAuth2 Desktop credentials\n"
                    "4. Download credentials.json\n"
                    f"5. Place it in:\n{self.settings_manager.config_dir}"
                ))
            return

        if self.calendar_manager.is_authenticated():
            # Already connected — disconnect
            self.calendar_manager.disconnect()
        else:
            print("[CALENDAR] Starting auth flow...")
            self.calendar_manager.authenticate()

    def _on_calendar_status(self, connected: bool):
        """Called from calendar manager thread when auth status changes."""
        print(f"[CALENDAR] Status: {'connected' if connected else 'disconnected'}")
        if self.main_window.window and self.main_window.window.winfo_exists():
            self.main_window.window.after(
                0, lambda: self.main_window.set_calendar_connected(connected))
        if connected:
            self.calendar_manager.start_polling()

    def _on_calendar_event(self, event_title: str, minutes_until: int):
        """Called from calendar polling thread when an upcoming event is found."""
        print(f"[CALENDAR] Event: '{event_title}' in {minutes_until} min")
        self.notification_manager.play_sound(
            volume=self.settings_manager.config.volume)
        self.notification_manager.show_calendar_notification(
            event_title=event_title,
            minutes_until=minutes_until,
            on_ok=lambda: print("[CALENDAR] User acknowledged"),
            on_skip=lambda: print("[CALENDAR] User skipped"),
        )

    def _on_test_notification(self):
        """Test notification with current settings"""
        import random
        import threading
        print("[TEST] Sending test notification...")

        # Get notification type from UI, not from config file
        notification_type = self.main_window.notification_var.get()
        print(f"[TEST] UI selected notification_type: {notification_type}")

        # If random is selected, pick a random type
        if notification_type == "random":
            notification_type = random.choice(["sound", "flash", "mixed"])
            print(f"🎲 Random notification: {notification_type}")

        # Callback to close notification after effects complete
        def on_test_stop():
            pass  # Just close, don't stop timer

        self.notification_manager.notify(
            notification_type=notification_type,
            volume=self.settings_manager.config.volume,
            on_stop=on_test_stop
        )

        # Auto-close notification after 3.5 seconds (allow flash/sound to complete)
        def auto_close_notification():
            time.sleep(3.5)
            if self.main_window.window and self.main_window.window.winfo_exists():
                self.main_window.window.after(0, self.notification_manager.close_notification_window)

        threading.Thread(target=auto_close_notification, daemon=True).start()

    def _on_rainbow_test(self):
        """Test alert effect with alert sound."""
        print("[ALERT TEST] Starting alert test...")
        self.notification_manager.show_notification_window(lambda: None)
        self.notification_manager.play_sound('alert.wav', self.settings_manager.config.volume)
        self.notification_manager.show_alert_flash(duration_seconds=3.0)

    def _on_update_available(self, version: str):
        """Handle update notification from UpdateChecker"""
        self.update_version = version
        print(f"[UPDATE] Update available: {version}")

        # Don't show dialog if user already skipped this version
        if self.settings_manager.config.skipped_update_version == version:
            print(f"[UPDATE] Version {version} was previously skipped by user")
            return

        if self.main_window.window and self.main_window.window.winfo_exists():
            self.main_window.window.after(0, self._show_update_dialog)

    def _show_update_dialog(self):
        """Show update dialog in main window"""
        from tkinter import messagebox

        version = self.update_version
        response = messagebox.askyesno(
            "Update Available",
            f"A new version ({version}) is available!\n\n"
            f"Current version: {APP_VERSION}\n\n"
            "Would you like to update now?\n"
            "(Click 'No' to skip this version)"
        )

        if response:
            self._perform_update()
        else:
            # Remember that user skipped this version so dialog doesn't reappear
            self.settings_manager.config.skipped_update_version = version
            self.settings_manager.save_config()
            print(f"[UPDATE] User skipped version {version}")

    def _perform_update(self):
        """Download and install update"""
        from tkinter import messagebox
        from pathlib import Path

        try:
            download_dir = Path(__file__).parent / ".update"
            assets_dir = self.settings_manager.assets_dir

            print("[UPDATE] Downloading update...")
            messagebox.showinfo("Updating", "Downloading new sounds...\nPlease wait.")

            # Download release
            success = self.update_checker.download_release(self.update_version, download_dir)

            if success:
                # Extract sounds
                zip_path = download_dir / "sounds.zip"
                if zip_path.exists():
                    self.update_checker.extract_sounds(zip_path, assets_dir / "sounds")
                    print("[UPDATE] Update completed successfully")
                    messagebox.showinfo("Success", "Sounds updated successfully!")
                else:
                    messagebox.showwarning("Update", "No sounds found in update")
            else:
                messagebox.showerror("Update Failed", "Could not download update")

        except Exception as e:
            print(f"[UPDATE] Error during update: {e}")
            messagebox.showerror("Error", f"Update failed: {e}")

    def _on_exit(self):
        """Обработчик выхода"""
        print("\n" + "=" * 50)
        print("[EXIT] Time to Pause Closed")
        print("=" * 50)
        self.timer.stop()
        self.main_window.close()
        self.tray_manager.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = BreakReminderApp()
    app.run()
