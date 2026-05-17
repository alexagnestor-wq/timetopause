# Break Reminder 🎯

Windows desktop app that reminds you to take breaks every N minutes. Shows notifications, plays sounds, and displays full-screen flashes to get your attention.

## Features

- ✅ **Customizable intervals** (20 sec, 30 min, 1 hour, 2 hours)
- ✅ **Multiple notification types** (sound only, flash only, mixed)
- ✅ **System tray integration** (minimal, always on background)
- ✅ **Settings GUI** (easy to configure)
- ✅ **Auto-startup** (planned)
- 🚧 **Custom asset library** (from GitHub, planned)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/break-reminder.git
   cd break-reminder
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python main.py
   ```

## Project Structure

```
break-reminder/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md              # This file
├── src/
│   ├── __init__.py
│   ├── settings.py        # Config management
│   ├── timer.py           # Background timer logic
│   ├── notifications.py   # Sound & flash effects
│   ├── tray_manager.py    # System tray integration
│   └── ui.py              # Settings GUI
└── assets/
    └── sounds/            # Custom sounds (to be added)
```

## Usage

### Run the app
```bash
python main.py
```

The app will:
1. Create a system tray icon (look for "B" icon)
2. Load saved settings from `%APPDATA%\BreakReminder\config.json`
3. Wait for you to click "Start" in the tray menu

### Tray Menu
- **▶ Start** - Start reminders
- **⏸ Stop** - Pause reminders
- **⚙ Settings** - Open settings window
- **❌ Exit** - Close app

### Settings Window
Choose:
- **Interval**: 20 sec, 30 min, 1 hour, 2 hours
- **Notification Type**: Sound only, Flash only, or Both

## Adding Custom Sounds

1. Create `.wav` files with your custom sounds
2. Place them in `%APPDATA%\BreakReminder\assets\sounds/`
3. Restart the app

Example structure:
```
%APPDATA%\BreakReminder\assets\sounds\
├── alert_1.wav
├── alert_2.wav
└── ...
```

## Future: Asset Library on GitHub

We'll create a separate repository with custom sounds and visual styles:
- Regular updates without app recompilation
- Users auto-download new assets
- Versioning & rollback support

## Testing

To test quickly:
1. Use "20 seconds" interval in Settings
2. Start the app
3. Wait 20 seconds for the first reminder

## Troubleshooting

**Issue**: Icon doesn't appear in tray
- **Solution**: Check if Python is installed correctly. Restart Windows.

**Issue**: Sound doesn't play
- **Solution**: Check if `pygame` is installed: `pip install pygame`

**Issue**: Flash screen is too bright
- **Solution**: Edit `src/notifications.py` and change the flash color/duration

## Requirements

- **Windows 7+** (tested on Windows 10/11)
- **Python 3.9+**
- See `requirements.txt` for pip packages

## License

MIT (or your preferred license)

## Author

Built with ❤️ for better productivity and health
