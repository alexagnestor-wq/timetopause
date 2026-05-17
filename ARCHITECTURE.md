# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    BREAK REMINDER APP                       │
│                        (main.py)                            │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Settings   │ │    Timer     │ │ Notification │
│  Manager     │ │              │ │   Manager    │
│              │ │ - Background │ │              │
│ - Config I/O │ │   thread     │ │ - Sound      │
│ - JSON save  │ │ - Countdown  │ │ - Flash      │
│ - Defaults   │ │ - Callback   │ │ - Combined   │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  Tray Manager    │
                │                  │
                │ - System tray    │
                │ - Menu items     │
                │ - Windows notify │
                └──────────────────┘
                         │
                         ▼
                ┌──────────────────┐
                │  Settings UI     │
                │                  │
                │ - Interval pick  │
                │ - Type select    │
                │ - Save/Cancel    │
                └──────────────────┘
```

## Data Flow Diagram

```
User clicks "Start"
        │
        ▼
TrayManager.on_start()
        │
        ▼
Timer.start()  ◄───── Creates background thread
        │
        ├─── Every N minutes ─────────┐
        │                             │
        ▼                             │
ReminderTimer._run()                 │
        │                             │
        ├─── time.sleep(interval) ◄──┘
        │
        ├─── on_reminder callback
        │
        ▼
NotificationManager.notify()
        │
        ├─── Play sound (pygame)
        │
        └─── Show flash (tkinter)
        │
        ▼
Windows notification toast
```

## File System Structure

```
User's Computer
│
├── C:\Users\USERNAME\AppData\Roaming\BreakReminder\
│   ├── config.json          ← User settings (persistent)
│   └── assets/
│       └── sounds/          ← Custom .wav files
│           ├── default.wav
│           ├── alert_1.wav
│           └── ...
│
└── C:\Users\USERNAME\Documents\...\TimeToPauseApp\
    ├── main.py              ← Run this
    ├── requirements.txt
    ├── run.bat
    └── src/
        ├── settings.py      ← Config management
        ├── timer.py         ← Background timer
        ├── notifications.py ← Sound + Flash
        ├── tray_manager.py  ← Windows integration
        └── ui.py            ← Settings window
```

## Component Details

### 1. SettingsManager (src/settings.py)
```
Purpose: Manage app configuration
┌─────────────────────────────┐
│ Config (dataclass)          │
├─────────────────────────────┤
│ - interval_minutes: int     │
│ - notification_type: str    │
│ - sound_enabled: bool       │
│ - flash_enabled: bool       │
│ - volume: int (0-100)       │
└─────────────────────────────┘
        │
        ├─ load_config()  → JSON file
        ├─ save_config()  → JSON file
        └─ update_*()     → Change settings
```

**Persistence:** JSON at `%APPDATA%\BreakReminder\config.json`

### 2. ReminderTimer (src/timer.py)
```
Purpose: Background countdown thread
┌─────────────────────────────┐
│ ReminderTimer               │
├─────────────────────────────┤
│ - callback: Callable        │
│ - interval_seconds: int     │
│ - is_running: bool          │
│ - thread: Thread            │
└─────────────────────────────┘
        │
        ├─ start()           → Spawn thread
        ├─ stop()            → Kill thread
        ├─ update_interval() → Restart with new interval
        └─ _run()            → Main loop (infinite until stop)
```

**Threading:** Uses `threading.Thread` with lock for thread-safe operations

### 3. NotificationManager (src/notifications.py)
```
Purpose: Handle sound and visual notifications
┌─────────────────────────────┐
│ NotificationManager         │
├─────────────────────────────┤
│ - assets_dir: Path          │
│ - sounds_dir: Path          │
│ - pygame.mixer initialized  │
└─────────────────────────────┘
        │
        ├─ play_sound()    → pygame mixer
        ├─ show_flash()    → tkinter full-screen window
        ├─ notify()        → Combined (sound + flash)
        └─ _system_beep()  → Fallback if no file
```

**Multi-threading:** Each sound/flash runs in daemon thread

### 4. TrayManager (src/tray_manager.py)
```
Purpose: System tray integration
┌─────────────────────────────┐
│ TrayManager                 │
├─────────────────────────────┤
│ - icon: pystray.Icon        │
│ - image: PIL.Image          │
│ - callbacks: on_start, etc  │
└─────────────────────────────┘
        │
        ├─ start()            → Create tray icon
        ├─ stop()             → Remove/hide
        ├─ setup_menu()       → Create menu items
        ├─ show_notification()→ Windows toast
        └─ _generate_default_icon() → Fallback image
```

**GUI Libraries:** `pystray` (tray) + `PIL` (image)

### 5. SettingsWindow (src/ui.py)
```
Purpose: GUI for user settings
┌──────────────────────────────┐
│ SettingsWindow               │
├──────────────────────────────┤
│ - window: tk.Tk              │
│ - interval_var: IntVar       │
│ - notification_var: StringVar│
└──────────────────────────────┘
        │
        ├─ show()      → Create and display window
        ├─ _on_save()  → Save to config + apply
        └─ Callbacks   → Update timer, etc
```

**GUI Framework:** `tkinter` (built-in Python)

## Threading Model

```
Main Thread
├── Initialization
│   ├── Load config
│   ├── Create managers
│   └── Setup tray icon
│
├── Event Loop (infinite)
│   ├── Handle tray clicks
│   ├── Display windows
│   └── Process events
│
└── On Exit
    └── Cleanup (stop timer, close windows, etc)

Background Threads (Daemon)
├── Timer Thread
│   ├── Sleep(interval)
│   ├── Call callback
│   └── Repeat
│
├── Sound Thread (per notification)
│   └── pygame.mixer.play()
│
└── Flash Thread (per notification)
    └── tkinter window.mainloop()
```

## Why This Architecture?

| Choice | Reason |
|--------|--------|
| **Threading** | Keep UI responsive while timer runs |
| **Config → JSON** | Simple, no database needed |
| **pystray** | Native Windows tray support |
| **pygame** | Reliable audio across Windows versions |
| **tkinter** | Built-in, no extra dependencies for basic UI |
| **Separation of concerns** | Each module has one job |

## Extensibility Points

```python
# Easy to add new features:

1. Custom notification types
   - In notify(): Add "vibrate", "email", etc.

2. New visual effects
   - Create src/visuals.py with different flash styles

3. Asset system
   - Replace load_sound() with GitHub downloader

4. Sound selection UI
   - Add dropdown in SettingsWindow

5. Schedule patterns
   - Extend Timer to support cron-like patterns

6. Statistics
   - Log when reminders triggered
   - Show usage dashboard
```

## Performance Considerations

| Component | Impact | Note |
|-----------|--------|------|
| **Timer thread** | Low | Sleeps most of the time |
| **Tray icon** | Minimal | Just pixel data in memory |
| **Sound playback** | Temporary | Only during notification |
| **Flash window** | Temporary | Only during notification |
| **Settings JSON** | Negligible | <1KB file |

**Memory usage estimate:** ~30-50 MB (mostly pygame + tk)

## Security Notes

- ✅ No network calls (until asset system)
- ✅ No elevated privileges needed
- ✅ Config stored in AppData (per-user, encrypted by Windows)
- ⚠️ Sound files loaded from disk without verification (will add hash checking with asset system)

---

**Next:** See ASSETS.md for details on sound library management.
