import tkinter as tk
import threading
import pygame
import random
import time
from pathlib import Path
from typing import Optional

class NotificationManager:
    """Управление звуком и визуальными эффектами"""

    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir
        self.sounds_dir = assets_dir / 'sounds'
        self.sounds_dir.mkdir(parents=True, exist_ok=True)

        # Инициализируем pygame для звука
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"Ошибка инициализации pygame: {e}")

    def play_sound(self, sound_filename: Optional[str] = None, volume: int = 100):
        """Воспроизвести звук в отдельном потоке"""
        threading.Thread(target=self._play_sound_thread, args=(sound_filename, volume), daemon=True).start()

    def _play_sound_thread(self, sound_filename: Optional[str], volume: int):
        """Внутренний метод для воспроизведения звука"""
        try:
            # Если файл не указан, выбираем рандомный из доступных
            if sound_filename is None:
                # Ищем все .wav файлы в папке
                wav_files = list(self.sounds_dir.glob('*.wav'))

                if wav_files:
                    # Выбираем рандомный звук
                    sound_filename = random.choice(wav_files).name
                    print(f"[SOUND] Playing random sound: {sound_filename}")
                else:
                    print("Нет звуков в папке. Используем системный сигнал.")
                    self._system_beep()
                    return

            sound_path = self.sounds_dir / sound_filename

            # Если файл не существует, используем системный звук
            if not sound_path.exists():
                print(f"Звук {sound_filename} не найден. Используем системный сигнал.")
                self._system_beep()
                return

            # Регулируем громкость (0.0 - 1.0)
            volume_float = min(100, volume) / 100.0
            pygame.mixer.music.load(str(sound_path))
            pygame.mixer.music.set_volume(volume_float)
            pygame.mixer.music.play()

            # Ждём пока звук закончится (с sleep чтобы не спин CPU)
            while pygame.mixer.music.get_busy():
                time.sleep(0.01)

        except Exception as e:
            print(f"Ошибка при воспроизведении звука: {e}")
            self._system_beep()

    def _system_beep(self):
        """Системный звуковой сигнал (fallback)"""
        try:
            import winsound
            winsound.Beep(1000, 500)  # 1000 Hz, 500 ms
        except Exception as e:
            print(f"Ошибка системного сигнала: {e}")

    def show_flash(self, duration_seconds: float = 3.0, text: str = "Time to pause!"):
        """Показать белую вспышку на весь экран"""
        threading.Thread(target=self._flash_thread, args=(duration_seconds, text), daemon=True).start()

    def _flash_thread(self, duration_seconds: float, text: str):
        """Внутренний метод для вспышки (в отдельном потоке)"""
        try:
            root = tk.Tk()

            # Получаем разрешение экрана
            root.update_idletasks()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()

            # Устанавливаем окно на весь экран
            root.geometry(f'{width}x{height}+0+0')
            root.attributes('-fullscreen', True)
            root.attributes('-topmost', True)
            root.configure(bg='white')
            root.attributes('-alpha', 1.0)  # Полная прозрачность в начале

            # Белый фон со всем содержимым
            main_frame = tk.Frame(root, bg='white')
            main_frame.pack(fill=tk.BOTH, expand=True)

            # Текст (в 5 раз меньше * 2 = 14 * 2 = 28)
            label = tk.Label(
                main_frame,
                text=text,
                font=('Arial', 28, 'bold'),
                bg='white',
                fg='black'
            )
            label.pack(expand=True)

            # Анимация fade-out за 3 секунды с большим количеством шагов для плавности
            fade_duration_ms = 3000
            fade_steps = 60  # 60 шагов = очень плавно
            step_duration_ms = fade_duration_ms // fade_steps

            def fade_out(step=0):
                if step < fade_steps:
                    progress = step / fade_steps
                    alpha = 1.0 - (progress ** 1.5)
                    root.attributes('-alpha', max(0, alpha))
                    root.after(step_duration_ms, lambda: fade_out(step + 1))
                else:
                    try:
                        root.destroy()
                    except:
                        pass

            root.after(1000, fade_out)
            root.mainloop()

        except Exception as e:
            print(f"Ошибка при отображении вспышки: {e}")

    def notify(self, notification_type: str = "mixed", sound_filename: Optional[str] = None, volume: int = 100):
        """Отправить уведомление (звук, вспышка или оба)"""
        if notification_type in ["sound", "mixed"]:
            self.play_sound(sound_filename, volume)

        if notification_type in ["flash", "mixed"]:
            self.show_flash(duration_seconds=3.0, text="Time to pause!")
