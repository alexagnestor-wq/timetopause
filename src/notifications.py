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

        self._root: Optional[tk.Tk] = None

        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"pygame init error: {e}")

        self.notification_window: Optional[tk.Toplevel] = None
        self.stop_callback = None

    def set_root_window(self, root: tk.Tk):
        """Register the main Tk root so we can schedule GUI work on it."""
        self._root = root

    def set_stop_callback(self, callback: Callable):
        self.stop_callback = callback

    # ------------------------------------------------------------------
    # Sound
    # ------------------------------------------------------------------

    def play_sound(self, sound_filename: Optional[str] = None, volume: int = 100, max_duration: int = 999):
        """Play sound in a background thread (audio is thread-safe)."""
        threading.Thread(
            target=self._play_sound_thread,
            args=(sound_filename, volume, max_duration),
            daemon=True
        ).start()

    def _play_sound_thread(self, sound_filename: Optional[str], volume: int, max_duration: int):
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
                if time.time() - start_time > max_duration:
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.01)

        except Exception as e:
            print(f"Sound playback error: {e}")
            self._system_beep()

    def _system_beep(self):
        try:
            import winsound
            winsound.Beep(1000, 300)
        except Exception as e:
            print(f"System beep error: {e}")

    # ------------------------------------------------------------------
    # Flash — must run on the main thread via Toplevel
    # ------------------------------------------------------------------

    def show_flash(self, duration_seconds: float = 3.0):
        """Schedule flash creation on the main Tk thread."""
        if self._root:
            self._root.after(0, lambda: self._create_flash(duration_seconds))
        else:
            # Fallback if root not set yet (should not normally happen)
            threading.Thread(target=self._flash_thread_fallback, args=(duration_seconds,), daemon=True).start()

    def _create_flash(self, duration_seconds: float):
        """Create fullscreen flash as a Toplevel on the main thread."""
        try:
            flash = tk.Toplevel(self._root)
            flash.attributes('-fullscreen', True)
            flash.attributes('-topmost', False)
            flash.configure(bg='white')
            flash.attributes('-alpha', 1.0)
            flash.overrideredirect(True)

            fade_steps = 60
            step_ms = max(1, int(duration_seconds * 1000 / fade_steps))

            def fade_out(step=0):
                if step < fade_steps:
                    progress = step / fade_steps
                    alpha = 1.0 - (progress ** 1.5)
                    try:
                        flash.attributes('-alpha', max(0.0, alpha))
                        flash.after(step_ms, lambda: fade_out(step + 1))
                    except Exception:
                        pass
                else:
                    try:
                        flash.destroy()
                    except Exception:
                        pass

            flash.after(500, fade_out)

        except Exception as e:
            print(f"Flash error: {e}")

    def _flash_thread_fallback(self, duration_seconds: float):
        """Legacy fallback — only used when root window is not available."""
        try:
            root = tk.Tk()
            root.update_idletasks()
            w, h = root.winfo_screenwidth(), root.winfo_screenheight()
            root.geometry(f'{w}x{h}+0+0')
            root.attributes('-fullscreen', True)
            root.configure(bg='white')
            root.attributes('-alpha', 1.0)

            fade_steps = 60
            step_ms = max(1, int(duration_seconds * 1000 / fade_steps))

            def fade_out(step=0):
                if step < fade_steps:
                    alpha = 1.0 - ((step / fade_steps) ** 1.5)
                    root.attributes('-alpha', max(0.0, alpha))
                    root.after(step_ms, lambda: fade_out(step + 1))
                else:
                    try:
                        root.destroy()
                    except Exception:
                        pass

            root.after(500, fade_out)
            root.mainloop()
        except Exception as e:
            print(f"Flash fallback error: {e}")

    # ------------------------------------------------------------------
    # Notification window — must run on the main thread via Toplevel
    # ------------------------------------------------------------------

    def show_notification_window(self, on_stop: Callable):
        """Schedule notification window creation on the main Tk thread."""
        if self._root:
            self._root.after(0, lambda: self._create_notification_window(on_stop))
        else:
            threading.Thread(
                target=self._notification_window_thread,
                args=(on_stop,),
                daemon=True
            ).start()

    def _create_notification_window(self, on_stop: Callable):
        """Create notification window as Toplevel on the main thread."""
        try:
            if self.notification_window and self.notification_window.winfo_exists():
                return

            self.notification_window = tk.Toplevel(self._root)
            self.notification_window.title("Time to Pause")
            self.notification_window.geometry("500x300")
            self.notification_window.resizable(False, False)
            self.notification_window.attributes('-topmost', True)

            main_frame = tk.Frame(self.notification_window, bg='#FFF176', padx=40, pady=40)
            main_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(
                main_frame,
                text="Time to make a pause!",
                font=('Arial', 28, 'bold'),
                bg='#FFF176',
                fg='#333333'
            ).pack(pady=(0, 20))

            tk.Label(
                main_frame,
                text="Take a break and rest your eyes",
                font=('Arial', 14),
                bg='#FFF176',
                fg='#666666'
            ).pack(pady=(0, 30))

            tk.Button(
                main_frame,
                text="STOP (I'm taking a break!)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#FF5252', fg='white',
                font=('Arial', 16, 'bold'),
                padx=30, pady=20,
                cursor='hand2', relief=tk.RAISED, bd=3
            ).pack(pady=10, fill=tk.X)

            tk.Button(
                main_frame,
                text="Continue (I'll take a break later)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#4CAF50', fg='white',
                font=('Arial', 12),
                padx=20, pady=10,
                cursor='hand2'
            ).pack(pady=5, fill=tk.X)

        except Exception as e:
            print(f"Notification window error: {e}")

    def _notification_window_thread(self, on_stop: Callable):
        """Legacy fallback — only used when root window is not available."""
        try:
            self.notification_window = tk.Tk()
            self.notification_window.title("Time to Pause")
            self.notification_window.geometry("500x300")
            self.notification_window.resizable(False, False)
            self.notification_window.attributes('-topmost', True)

            main_frame = tk.Frame(self.notification_window, bg='#FFF176', padx=40, pady=40)
            main_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(
                main_frame,
                text="Time to make a pause!",
                font=('Arial', 28, 'bold'),
                bg='#FFF176', fg='#333333'
            ).pack(pady=(0, 20))

            tk.Label(
                main_frame,
                text="Take a break and rest your eyes",
                font=('Arial', 14),
                bg='#FFF176', fg='#666666'
            ).pack(pady=(0, 30))

            tk.Button(
                main_frame,
                text="STOP (I'm taking a break!)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#FF5252', fg='white',
                font=('Arial', 16, 'bold'),
                padx=30, pady=20,
                cursor='hand2', relief=tk.RAISED, bd=3
            ).pack(pady=10, fill=tk.X)

            tk.Button(
                main_frame,
                text="Continue (I'll take a break later)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#4CAF50', fg='white',
                font=('Arial', 12),
                padx=20, pady=10,
                cursor='hand2'
            ).pack(pady=5, fill=tk.X)

            while self.notification_window and self.notification_window.winfo_exists():
                try:
                    self.notification_window.update()
                except Exception:
                    break
                time.sleep(0.01)

        except Exception as e:
            print(f"Notification window error: {e}")
        finally:
            if self.notification_window:
                try:
                    self.notification_window.destroy()
                except Exception:
                    pass
            self.notification_window = None

    def _on_notification_stop(self, on_stop: Callable):
        """Handle notification close (called on main thread via button click)."""
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
        except Exception:
            pass

        if self.notification_window:
            try:
                self.notification_window.destroy()
            except Exception:
                pass
            self.notification_window = None

        if on_stop:
            on_stop()

    def close_notification_window(self):
        """Close notification window from the main thread."""
        if self.notification_window:
            try:
                self.notification_window.destroy()
            except Exception:
                pass
            self.notification_window = None

    # ------------------------------------------------------------------
    # Combined notify
    # ------------------------------------------------------------------

    def notify(
        self,
        notification_type: str = "mixed",
        sound_filename: Optional[str] = None,
        volume: int = 100,
        on_stop: Callable = None
    ):
        print(f"[NOTIFY] Called with notification_type: {notification_type}")

        self.show_notification_window(on_stop)

        if notification_type in ("sound", "mixed"):
            self.play_sound(sound_filename, volume, max_duration=999)

        if notification_type in ("flash", "mixed"):
            self.show_flash(duration_seconds=3.0)
