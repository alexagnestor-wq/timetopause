import threading
import time
from typing import Callable, Optional

class ReminderTimer:
    """Фоновый таймер для напоминаний"""

    def __init__(self, callback: Callable, interval_minutes: float = 30):
        self.callback = callback
        # Поддерживаем как целые минуты, так и доли (для секунд)
        self.interval_seconds = interval_minutes * 60
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self):
        """Запустить таймер"""
        with self._lock:
            if self.is_running:
                return

            self.is_running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print(f"[TIMER] Timer started (interval: {self.interval_seconds // 60} min)")

    def stop(self):
        """Остановить таймер"""
        with self._lock:
            self.is_running = False
            print("[TIMER] Timer stopped")

    def _run(self):
        """Основной цикл таймера (в отдельном потоке)"""
        while self.is_running:
            time.sleep(self.interval_seconds)
            if self.is_running:  # Проверяем ещё раз после sleep
                self.callback()

    def update_interval(self, interval_minutes: float):
        """Обновить интервал таймера"""
        with self._lock:
            self.interval_seconds = interval_minutes * 60

        # Красивый вывод для секунд и минут
        if interval_minutes < 1:
            display = f"{int(self.interval_seconds)} sec"
        elif interval_minutes == 1:
            display = "1 min"
        else:
            display = f"{int(interval_minutes)} min"
        print(f"[INTERVAL] Updated: {display}")

    def is_active(self) -> bool:
        """Проверить, активен ли таймер"""
        return self.is_running
