import tkinter as tk
import threading
import pygame
import random
import time
from pathlib import Path
from typing import Optional, Callable

class NotificationManager:
    """Manage sound and visual effects"""

    def __init__(self, assets_dir: Path):
        self.assets_dir = assets_dir
        self.sounds_dir = assets_dir / 'sounds'
        self.sounds_dir.mkdir(parents=True, exist_ok=True)

        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"pygame init error: {e}")

        self.notification_window = None
        self.stop_callback = None

    def set_stop_callback(self, callback: Callable):
        """Set callback for STOP button"""
        self.stop_callback = callback

    def play_sound(self, sound_filename: Optional[str] = None, volume: int = 100, max_duration: int = 999):
        """Play sound in separate thread (with duration limit)"""
        threading.Thread(
            target=self._play_sound_thread,
            args=(sound_filename, volume, max_duration),
            daemon=True
        ).start()

    def _play_sound_thread(self, sound_filename: Optional[str], volume: int, max_duration: int):
        """Internal method for sound playback"""
        try:
            if sound_filename is None:
                wav_files = list(self.sounds_dir.glob('*.wav'))

                if wav_files:
                    sound_filename = random.choice(wav_files).name
                    print(f"Playing: {sound_filename}")
                else:
                    print("No sounds found. Using system beep.")
                    self._system_beep()
                    return

            sound_path = self.sounds_dir / sound_filename

            if not sound_path.exists():
                print(f"Sound {sound_filename} not found. Using system beep.")
                self._system_beep()
                return

            volume_float = min(100, volume) / 100.0
            pygame.mixer.music.load(str(sound_path))
            pygame.mixer.music.set_volume(volume_float)
            pygame.mixer.music.play()

            start_time = time.time()
            while pygame.mixer.music.get_busy():
                elapsed = time.time() - start_time
                if elapsed > max_duration:
                    pygame.mixer.music.stop()
                    print(f"Sound stopped after {max_duration} seconds")
                    break
                time.sleep(0.01)

        except Exception as e:
            print(f"Sound playback error: {e}")
            self._system_beep()

    def _system_beep(self):
        """System beep (fallback)"""
        try:
            import winsound
            winsound.Beep(1000, 300)
        except Exception as e:
            print(f"System beep error: {e}")

    def show_flash(self, duration_seconds: float = 3.0):
        """Show white flash on full screen (behind notification)"""
        threading.Thread(
            target=self._flash_thread,
            args=(duration_seconds,),
            daemon=True
        ).start()

    def _flash_thread(self, duration_seconds: float):
        """Internal method for flash effect"""
        try:
            root = tk.Tk()

            root.update_idletasks()
            width = root.winfo_screenwidth()
            height = root.winfo_screenheight()

            root.geometry(f'{width}x{height}+0+0')
            root.attributes('-fullscreen', True)
            root.attributes('-topmost', False)
            root.configure(bg='white')
            root.attributes('-alpha', 1.0)

            fade_duration_ms = int(duration_seconds * 1000)
            fade_steps = 60
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

            root.after(500, fade_out)
            root.mainloop()

        except Exception as e:
            print(f"Flash error: {e}")

    def show_notification_window(self, on_stop: Callable):
        """Show notification window with text and STOP button"""
        threading.Thread(
            target=self._notification_window_thread,
            args=(on_stop,),
            daemon=True
        ).start()

    def _notification_window_thread(self, on_stop: Callable):
        """Internal method for notification window"""
        try:
            self.notification_window = tk.Tk()
            self.notification_window.title("Time to Pause")
            self.notification_window.geometry("500x300")
            self.notification_window.resizable(False, False)

            self.notification_window.attributes('-topmost', True)

            main_frame = tk.Frame(
                self.notification_window,
                bg='#FFF176',
                padx=40,
                pady=40
            )
            main_frame.pack(fill=tk.BOTH, expand=True)

            title_label = tk.Label(
                main_frame,
                text="Time to make a pause!",
                font=('Arial', 28, 'bold'),
                bg='#FFF176',
                fg='#333333'
            )
            title_label.pack(pady=(0, 20))

            sub_label = tk.Label(
                main_frame,
                text="Take a break and rest your eyes",
                font=('Arial', 14),
                bg='#FFF176',
                fg='#666666'
            )
            sub_label.pack(pady=(0, 30))

            stop_btn = tk.Button(
                main_frame,
                text="STOP (I'm taking a break!)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#FF5252',
                fg='white',
                font=('Arial', 16, 'bold'),
                padx=30,
                pady=20,
                cursor='hand2',
                relief=tk.RAISED,
                bd=3
            )
            stop_btn.pack(pady=10, fill=tk.X)

            continue_btn = tk.Button(
                main_frame,
                text="Continue (I'll take a break later)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#4CAF50',
                fg='white',
                font=('Arial', 12),
                padx=20,
                pady=10,
                cursor='hand2'
            )
            continue_btn.pack(pady=5, fill=tk.X)

            # Don't block with mainloop - use update loop instead
            # This allows other threads (flash, sound) to run
            start_time = time.time()
            while self.notification_window and self.notification_window.winfo_exists():
                try:
                    self.notification_window.update()
                except:
                    break
                time.sleep(0.01)  # Small delay to prevent CPU spinning

        except Exception as e:
            print(f"Notification window error: {e}")
        finally:
            if self.notification_window:
                try:
                    self.notification_window.destroy()
                except:
                    pass
            self.notification_window = None

    def _on_notification_stop(self, on_stop: Callable):
        """Handle notification close"""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                print("Sound stopped by notification close")
        except:
            pass

        if self.notification_window:
            try:
                self.notification_window.destroy()
            except:
                pass
            self.notification_window = None

        if on_stop:
            on_stop()

    def notify(
        self,
        notification_type: str = "mixed",
        sound_filename: Optional[str] = None,
        volume: int = 100,
        on_stop: Callable = None
    ):
        """Send notification (sound, flash, and/or window with STOP button)"""

        print(f"[NOTIFY] Called with notification_type: {notification_type}")

        self.show_notification_window(on_stop)
        print(f"[NOTIFY] Notification window shown")

        if notification_type in ["sound", "mixed"]:
            print(f"[NOTIFY] Playing sound (type={notification_type})")
            self.play_sound(sound_filename, volume, max_duration=999)
        else:
            print(f"[NOTIFY] NOT playing sound (type={notification_type})")

        if notification_type in ["flash", "mixed"]:
            print(f"[NOTIFY] Showing flash (type={notification_type})")
            self.show_flash(duration_seconds=3.0)
        else:
            print(f"[NOTIFY] NOT showing flash (type={notification_type})")
