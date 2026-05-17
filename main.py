#!/usr/bin/env python3
"""
Break Reminder - Windows Desktop App
Напоминает пользователю сделать паузу в работе
"""

import sys
import time
from pathlib import Path

# Добавим текущую папку в path для импортов
sys.path.insert(0, str(Path(__file__).parent))

from src.settings import SettingsManager
from src.timer import ReminderTimer
from src.notifications import NotificationManager
from src.tray_manager import TrayManager
from src.ui import MainWindow, SettingsWindow
from src.updater import UpdateChecker
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
        self.main_window = MainWindow(
            self.settings_manager,
            on_start=self._on_timer_start,
            on_stop=self._on_timer_stop,
            on_minimize=self._on_window_minimize
        )
        self.settings_window = SettingsWindow(
            self.settings_manager,
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

        self.tray_manager.start()
        self.main_window.show()

        # Главное окно уже блокирует поток

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
        print(f"\n[REMINDER] REMINDER! ({time.strftime('%H:%M:%S')})")

        self.notification_manager.notify(
            notification_type=config.notification_type,
            volume=config.volume
        )

        self.tray_manager.show_notification(
            "Break Reminder",
            "Time to take a break! 💪"
        )

        # Автоматически停止 таймер после уведомления (для теста)
        print("[AUTO-STOP] Auto-stopping timer after notification (test mode)")
        self._on_timer_stop()

        # Schedule UI updates on the main thread (tkinter is not thread-safe)
        if self.main_window.window and self.main_window.window.winfo_exists():
            self.main_window.window.after(0, self._update_ui_after_reminder)

    def _update_ui_after_reminder(self):
        """Update UI on main thread after reminder"""
        self.main_window.is_running = False
        self.main_window.start_btn.config(state='normal')
        self.main_window.stop_btn.config(state='disabled')
        self.main_window.status_label.config(text="Status: Stopped", fg="#888888")

    def _on_settings(self):
        """Обработчик открытия окна настроек"""
        print("⚙ Opening settings...")
        self.settings_window.show()

    def _on_settings_apply(self, interval: int, notification_type: str):
        """Обработчик применения новых настроек"""
        print(f"✓ Settings applied: interval={interval} min, type={notification_type}")

        # Перезапустить таймер с новым интервалом
        self.timer.update_interval(interval)

    def _on_update_available(self, version: str):
        """Handle update notification from UpdateChecker"""
        self.update_version = version
        print(f"[UPDATE] Update available: {version}")

        # Show notification to user
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
            "Would you like to update now?"
        )

        if response:
            self._perform_update()

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
