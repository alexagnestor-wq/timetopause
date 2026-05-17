# Quick Start Guide 🚀

## Installation & First Run (2 minutes)

### 1. Install Python Dependencies
```bash
cd break-reminder
pip install -r requirements.txt
```

**Or** just run:
```bash
run.bat
```

### 2. Start the App
```bash
python main.py
```

You should see:
- ✅ Console output: "Break Reminder Started"
- ✅ "B" icon appears in system tray (bottom-right corner)

### 3. Activate from Tray Menu
- Right-click the "B" icon in tray
- Click "▶ Start"
- You'll see a notification: "Reminder started! You'll be notified every 30 minutes"

### 4. Test with 20-Second Interval
- Right-click "B" icon → "⚙ Settings"
- Select "20 seconds (test)"
- Click "Save"
- Wait 20 seconds...
- 🔔 **BOOM!** White flash + system beep

## What Just Happened?

| Component | What It Does |
|-----------|-------------|
| **main.py** | Entry point - runs the whole app |
| **System Tray** | "B" icon in bottom-right corner |
| **Timer** | Counts down in background thread |
| **Reminder Callback** | Triggers sound + flash when time's up |
| **Settings** | Let you customize interval & notification type |

## Project Files Overview

```
TimeToPauseApp/
├── main.py                  ← RUN THIS
├── requirements.txt         ← Dependencies
├── run.bat                  ← Alternative launcher
├── test_components.py       ← Test each component
├── README.md                ← Full documentation
├── ASSETS.md                ← Sound/visual management
├── QUICKSTART.md            ← This file
└── src/
    ├── settings.py          ← Load/save config
    ├── timer.py             ← Background countdown
    ├── notifications.py     ← Sound & flash
    ├── tray_manager.py      ← System tray UI
    └── ui.py                ← Settings window
```

## Common Tasks

### 🎵 Add Custom Sound
1. Get a `.wav` file (e.g., from Freesound.org)
2. Copy to: `%APPDATA%\BreakReminder\assets\sounds\myalert.wav`
3. Edit `main.py` line where it says `sound_filename=...` to use your file
4. Restart app

### ⚙ Change Defaults
Edit `src/settings.py` and change:
```python
@dataclass
class Config:
    interval_minutes: int = 30  # Change here
    notification_type: str = "mixed"  # Or "sound" / "flash"
```

### 🧪 Test Everything
```bash
python test_components.py
```

This will:
- ✅ Test config loading
- ✅ Test sound playback
- ✅ Test flash screen (3 seconds)
- ✅ Test timer (5 second intervals)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Icon doesn't appear** | Restart Windows, check System Tray settings |
| **No sound** | Make sure volume is on, check `pygame` installed |
| **Settings don't save** | Check write permissions to `%APPDATA%` |
| **App crashes** | Run `python test_components.py` to diagnose |

## Next Steps

1. ✅ **MVP is working** - Try it out!
2. 🎨 **Create custom icon** - Replace "B" with your design
3. 🎵 **Add custom sounds** - See ASSETS.md
4. 🚀 **Setup auto-startup** - See README.md (coming soon)
5. 📦 **Create .exe** - Use PyInstaller to make standalone .exe

## Need Help?

- **Python not installed?** → https://www.python.org/downloads/
- **Can't find System Tray?** → Windows 10/11: Settings → Taskbar → Show hidden icons
- **Dependencies failing?** → Try: `pip install --upgrade pip` then reinstall

---

**You're all set!** 🎯 Run `python main.py` and start taking breaks!
