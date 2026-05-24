import tkinter as tk
import threading
import pygame
import random
import time
from pathlib import Path
from typing import Optional, Callable

_RAINBOW = [
    '#FF0000', '#FF5500', '#FF9900', '#FFCC00', '#FFFF00',
    '#AAFF00', '#00FF00', '#00FFAA', '#00FFFF', '#00AAFF',
    '#0055FF', '#5500FF', '#AA00FF', '#FF00AA', '#FF0055',
]
_PIXEL_SIZE = 64
_FRAME_MS = 50  # 20fps


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
    # Alert text flash
    # ------------------------------------------------------------------

    def show_alert_flash(self, duration_seconds: float = 3.0):
        if self._root:
            self._root.after(0, lambda: self._create_alert_flash(duration_seconds))

    def _create_alert_flash(self, duration_seconds: float):
        try:
            flash = tk.Toplevel(self._root)
            flash.attributes('-fullscreen', True)
            flash.attributes('-topmost', True)
            flash.attributes('-alpha', 0.0)
            flash.overrideredirect(True)
            flash.configure(bg='white')

            sw = flash.winfo_screenwidth()
            sh = flash.winfo_screenheight()

            canvas = tk.Canvas(flash, width=sw, height=sh, bg='white', highlightthickness=0)
            canvas.pack()
            canvas.create_text(
                sw // 2, sh // 2,
                text="FAAAAAAAAA!",
                font=('Karmatic Arcade', 100),
                fill='#000000',
                anchor='center'
            )

            if self.notification_window and self.notification_window.winfo_exists():
                self.notification_window.lift()

            total_frames = int(duration_seconds * 20)
            fade_in  = max(1, int(0.15 * 20))
            fade_out = max(1, int(1.0  * 20))
            frame = [0]

            def animate():
                f = frame[0]
                if f >= total_frames:
                    try:
                        flash.destroy()
                    except Exception:
                        pass
                    return
                if f < fade_in:
                    alpha = f / fade_in
                elif f > total_frames - fade_out:
                    alpha = (total_frames - f) / fade_out
                else:
                    alpha = 1.0
                try:
                    flash.attributes('-alpha', max(0.0, min(1.0, alpha)))
                except Exception:
                    pass
                frame[0] += 1
                flash.after(50, animate)

            animate()

        except Exception as e:
            print(f"Alert flash error: {e}")

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
            flash.attributes('-topmost', True)
            flash.configure(bg='white')
            flash.attributes('-alpha', 1.0)
            flash.overrideredirect(True)

            # Keep notification popup above the flash
            if self.notification_window and self.notification_window.winfo_exists():
                self.notification_window.lift()

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
    # Rainbow flash — must run on the main thread via Toplevel
    # ------------------------------------------------------------------

    def show_rainbow_flash(self, duration_seconds: float = 4.0):
        """Schedule pixel rainbow animation on the main Tk thread."""
        if self._root:
            self._root.after(0, lambda: self._create_rainbow_flash(duration_seconds))

    def _create_rainbow_flash(self, duration_seconds: float):
        """Fullscreen pixel-grid rainbow wave animation."""
        try:
            flash = tk.Toplevel(self._root)
            flash.attributes('-fullscreen', True)
            flash.attributes('-topmost', True)
            flash.attributes('-alpha', 0.0)
            flash.overrideredirect(True)
            flash.configure(bg='black')

            if self.notification_window and self.notification_window.winfo_exists():
                self.notification_window.lift()

            sw = flash.winfo_screenwidth()
            sh = flash.winfo_screenheight()

            canvas = tk.Canvas(flash, width=sw, height=sh, bg='black', highlightthickness=0)
            canvas.pack()

            PS = _PIXEL_SIZE
            cols = sw // PS + 1
            rows = sh // PS + 1
            nc = len(_RAINBOW)

            rects = []
            for r in range(rows):
                for c in range(cols):
                    rid = canvas.create_rectangle(
                        c * PS, r * PS, (c + 1) * PS, (r + 1) * PS,
                        fill=_RAINBOW[0], outline=''
                    )
                    rects.append((rid, r, c))

            total_frames = max(1, int(duration_seconds * (1000 / _FRAME_MS)))
            fade_in  = max(1, int(0.2  * (1000 / _FRAME_MS)))
            fade_out = max(1, int(1.0  * (1000 / _FRAME_MS)))
            frame = [0]

            def animate():
                f = frame[0]
                if f >= total_frames:
                    try:
                        flash.destroy()
                    except Exception:
                        pass
                    return

                if f < fade_in:
                    alpha = f / fade_in
                elif f > total_frames - fade_out:
                    alpha = (total_frames - f) / fade_out
                else:
                    alpha = 1.0
                try:
                    flash.attributes('-alpha', max(0.0, min(1.0, alpha)))
                except Exception:
                    pass

                for rid, r, c in rects:
                    canvas.itemconfig(rid, fill=_RAINBOW[(c + r + f) % nc])

                frame[0] += 1
                flash.after(_FRAME_MS, animate)

            animate()

        except Exception as e:
            print(f"Rainbow flash error: {e}")

    # ------------------------------------------------------------------
    # Notification window — must run on the main thread via Toplevel
    # ------------------------------------------------------------------

    def show_notification_window(self, on_stop: Callable):
        """Schedule notification window creation on the main Tk thread."""
        if self._root:
            self._root.after(500, lambda: self._create_notification_window(on_stop))
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
                try:
                    self.notification_window.destroy()
                except Exception:
                    pass
                self.notification_window = None

            self.notification_window = tk.Toplevel(self._root)
            self.notification_window.title("Time to Pause")
            self.notification_window.geometry("500x320")
            self.notification_window.resizable(False, False)
            self.notification_window.attributes('-topmost', True)

            # Center window on screen
            self.notification_window.update_idletasks()
            x = (self.notification_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.notification_window.winfo_screenheight() // 2) - (320 // 2)
            self.notification_window.geometry(f"500x320+{x}+{y}")

            main_frame = tk.Frame(self.notification_window, bg='#ffffff', padx=40, pady=30)
            main_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(
                main_frame,
                text="TIME TO\nMAKE A PAUSE!",
                font=('Karmatic Arcade', 28),
                bg='#ffffff',
                fg='#000000',
                justify='center'
            ).pack(pady=(0, 15))

            tk.Label(
                main_frame,
                text="Take a break and rest your eyes",
                font=('Arial', 12),
                bg='#ffffff',
                fg='#333333'
            ).pack(pady=(0, 20))

            tk.Button(
                main_frame,
                text="STOP (I'm taking a break!)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#000000', fg='#ffffff',
                font=('Arial', 11, 'bold'),
                padx=20, pady=12,
                cursor='hand2', relief='solid', bd=2
            ).pack(fill=tk.X, pady=(0, 8))

            tk.Button(
                main_frame,
                text="Continue (I'll take a break later)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#ffffff', fg='#000000',
                font=('Arial', 11, 'bold'),
                padx=20, pady=12,
                cursor='hand2', relief='solid', bd=2
            ).pack(fill=tk.X)

        except Exception as e:
            print(f"Notification window error: {e}")

    def _notification_window_thread(self, on_stop: Callable):
        """Legacy fallback — only used when root window is not available."""
        try:
            self.notification_window = tk.Tk()
            self.notification_window.title("Time to Pause")
            self.notification_window.geometry("500x320")
            self.notification_window.resizable(False, False)
            self.notification_window.attributes('-topmost', True)

            # Center window on screen
            self.notification_window.update_idletasks()
            x = (self.notification_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.notification_window.winfo_screenheight() // 2) - (320 // 2)
            self.notification_window.geometry(f"500x320+{x}+{y}")

            main_frame = tk.Frame(self.notification_window, bg='#ffffff', padx=40, pady=30)
            main_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(
                main_frame,
                text="TIME TO\nMAKE A PAUSE!",
                font=('Karmatic Arcade', 28),
                bg='#ffffff', fg='#000000',
                justify='center'
            ).pack(pady=(0, 15))

            tk.Label(
                main_frame,
                text="Take a break and rest your eyes",
                font=('Arial', 12),
                bg='#ffffff', fg='#333333'
            ).pack(pady=(0, 20))

            tk.Button(
                main_frame,
                text="STOP (I'm taking a break!)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#000000', fg='#ffffff',
                font=('Arial', 11, 'bold'),
                padx=20, pady=12,
                cursor='hand2', relief='solid', bd=2
            ).pack(fill=tk.X, pady=(0, 8))

            tk.Button(
                main_frame,
                text="Continue (I'll take a break later)",
                command=lambda: self._on_notification_stop(on_stop),
                bg='#ffffff', fg='#000000',
                font=('Arial', 11, 'bold'),
                padx=20, pady=12,
                cursor='hand2', relief='solid', bd=2
            ).pack(fill=tk.X)

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
    # Calendar notification window
    # ------------------------------------------------------------------

    def show_calendar_notification(self, event_title: str, minutes_until: int,
                                   on_ok: Callable, on_skip: Callable):
        """Show calendar event alert on the main Tk thread."""
        if self._root:
            self._root.after(0, lambda: self._create_calendar_notification(
                event_title, minutes_until, on_ok, on_skip))

    def _create_calendar_notification(self, event_title: str, minutes_until: int,
                                      on_ok: Callable, on_skip: Callable):
        try:
            if self.notification_window and self.notification_window.winfo_exists():
                try:
                    self.notification_window.destroy()
                except Exception:
                    pass
                self.notification_window = None

            win = tk.Toplevel(self._root)
            self.notification_window = win
            win.title("Upcoming Call")
            win.geometry("500x340")
            win.resizable(False, False)
            win.attributes('-topmost', True)

            win.update_idletasks()
            x = (win.winfo_screenwidth()  // 2) - 250
            y = (win.winfo_screenheight() // 2) - 170
            win.geometry(f"500x340+{x}+{y}")

            main_frame = tk.Frame(win, bg='#ffffff', padx=40, pady=30)
            main_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(
                main_frame,
                text="UPCOMING CALL!",
                font=('Karmatic Arcade', 24),
                bg='#ffffff', fg='#000000',
                justify='center'
            ).pack(pady=(0, 10))

            tk.Label(
                main_frame,
                text=event_title,
                font=('Arial', 13, 'bold'),
                bg='#ffffff', fg='#000000',
                wraplength=400, justify='center'
            ).pack(pady=(0, 4))

            tk.Label(
                main_frame,
                text=f"starts in {minutes_until} minute{'s' if minutes_until != 1 else ''}",
                font=('Arial', 11),
                bg='#ffffff', fg='#555555'
            ).pack(pady=(0, 20))

            def _ok():
                try:
                    win.destroy()
                except Exception:
                    pass
                self.notification_window = None
                if on_ok:
                    on_ok()

            def _skip():
                try:
                    win.destroy()
                except Exception:
                    pass
                self.notification_window = None
                if on_skip:
                    on_skip()

            tk.Button(
                main_frame,
                text="OK, THANKS!",
                command=_ok,
                bg='#000000', fg='#ffffff',
                font=('Arial', 11, 'bold'),
                padx=20, pady=12,
                cursor='hand2', relief='solid', bd=2
            ).pack(fill=tk.X, pady=(0, 8))

            tk.Button(
                main_frame,
                text="I'LL SKIP THIS ONE",
                command=_skip,
                bg='#ffffff', fg='#000000',
                font=('Arial', 11, 'bold'),
                padx=20, pady=12,
                cursor='hand2', relief='solid', bd=2
            ).pack(fill=tk.X)

        except Exception as e:
            print(f"Calendar notification error: {e}")

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

        # Pre-select sound so we can decide which visual effect to show
        selected_sound = sound_filename
        if notification_type in ("sound", "mixed") and selected_sound is None:
            wav_files = list(self.sounds_dir.glob('*.wav'))
            if wav_files:
                selected_sound = random.choice(wav_files).name
                print(f"Pre-selected sound: {selected_sound}")

        if notification_type in ("sound", "mixed"):
            self.play_sound(selected_sound, volume, max_duration=999)

        is_rainbow = selected_sound and 'taste-the-rainbow' in selected_sound.lower()
        is_alert   = selected_sound and 'alert' in selected_sound.lower()

        if is_rainbow:
            self.show_rainbow_flash(duration_seconds=3.0)
        elif is_alert:
            self.show_alert_flash(duration_seconds=3.0)
        elif notification_type in ("flash", "mixed"):
            self.show_flash(duration_seconds=3.0)
