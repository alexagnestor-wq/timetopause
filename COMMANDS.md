# Quick Commands Reference

## Installation

```bash
# Navigate to project folder
cd C:\Users\suprunov-a\Documents\MaProjects\Claude\TimeToPauseApp

# Install dependencies
pip install -r requirements.txt
```

## Running the App

### Option 1: Quick (Windows)
```bash
run.bat
```

### Option 2: Direct Python
```bash
python main.py
```

### Option 3: From anywhere (after installation)
```bash
python C:\Users\suprunov-a\Documents\MaProjects\Claude\TimeToPauseApp\main.py
```

## Testing

### Test all components
```bash
python test_components.py
```

This will:
- ✅ Test config loading/saving
- ✅ Test sound playback
- ✅ Test flash screen (3 seconds)
- ✅ Test timer (5 second intervals)

### Individual component tests (manual)
```python
# Test just the timer
python -c "from src.timer import ReminderTimer; import time; t = ReminderTimer(lambda: print('REMINDER!'), 1); t.start(); time.sleep(65)"

# Test just sound
python -c "from src.notifications import NotificationManager; from pathlib import Path; nm = NotificationManager(Path('.')); nm.play_sound()"

# Test just flash
python -c "from src.notifications import NotificationManager; from pathlib import Path; nm = NotificationManager(Path('.')); nm.show_flash(3)"
```

## Configuration

### View current settings
```bash
# Open config file
notepad %APPDATA%\BreakReminder\config.json
```

### Reset to defaults
```bash
# Delete config (will recreate with defaults on next run)
del %APPDATA%\BreakReminder\config.json
```

### Change intervals in code
Edit `src/settings.py`:
```python
@dataclass
class Config:
    interval_minutes: int = 30  # Change this number
```

## File Management

### Locate config folder
```bash
explorer %APPDATA%\BreakReminder
```

### Add custom sound
```bash
# Copy .wav file to sounds folder
copy path\to\your\sound.wav %APPDATA%\BreakReminder\assets\sounds\
```

### Clear all data
```bash
# Delete entire BreakReminder folder (will recreate on next run)
rmdir /s /q %APPDATA%\BreakReminder
```

## Troubleshooting Commands

### Check Python version
```bash
python --version
```

### Check installed packages
```bash
pip list | findstr pystray
pip list | findstr pygame
pip list | findstr pillow
```

### Reinstall dependencies
```bash
pip uninstall pystray pygame pillow -y
pip install -r requirements.txt
```

### Clear pip cache
```bash
pip cache purge
pip install --force-reinstall -r requirements.txt
```

## Packaging (Future)

### Create standalone .exe
```bash
# Install pyinstaller
pip install pyinstaller

# Create .exe
pyinstaller --onefile --windowed --icon=icon.ico main.py

# .exe will be in: dist\main.exe
```

### Create with custom settings
```bash
pyinstaller \
  --onefile \
  --windowed \
  --name "BreakReminder" \
  --icon icon.ico \
  --add-data "assets:assets" \
  main.py
```

## Development Commands

### Format code (optional)
```bash
pip install black
black src/
black main.py
```

### Check code quality
```bash
pip install pylint
pylint src/
```

### Run with debug output
```bash
python main.py 2>&1 | tee debug.log
```

## Project Info

### View all files
```bash
tree /F
# Or on Windows without tree:
dir /s /b
```

### Count lines of code
```bash
findstr /r "." src\*.py | find /c ":"
```

### Verify project structure
```bash
python -c "import os; [print(f) for f in os.listdir('.') if not f.startswith('.')]"
```

## Environment Variables (Optional)

### Set Python path (if needed)
```bash
set PYTHONPATH=%PYTHONPATH%;C:\Users\suprunov-a\Documents\MaProjects\Claude\TimeToPauseApp
```

### Check APPDATA location
```bash
echo %APPDATA%
```

## IDE Setup (if using VS Code)

### Create workspace file (optional)
Create `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "C:\\Users\\suprunov-a\\AppData\\Local\\Programs\\Python\\Python39\\python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true
}
```

## Git Commands (if using version control)

```bash
# Initialize repo
git init

# Add all files
git add .

# First commit
git commit -m "Initial MVP commit - Break Reminder"

# Create .gitignore
echo __pycache__/ > .gitignore
echo *.pyc >> .gitignore
echo .vscode/ >> .gitignore
echo dist/ >> .gitignore
echo build/ >> .gitignore
```

## Documentation

### Generate documentation
```bash
# View main docs
notepad README.md
notepad QUICKSTART.md
notepad ARCHITECTURE.md
notepad SUMMARY.md
```

### View project overview
```bash
# Open in default browser
start break_reminder_overview.html
```

## Common Issues & Solutions

### "Module not found: pystray"
```bash
pip install pystray --upgrade
```

### "Module not found: pygame"
```bash
pip install pygame --upgrade
```

### "Icon not appearing in tray"
```bash
# Restart Windows, then:
python main.py
# Check notification area in bottom-right
```

### "Settings don't save"
```bash
# Check write permissions:
icacls %APPDATA%\BreakReminder /grant %USERNAME%:F

# Or delete and let app recreate:
rmdir /s /q %APPDATA%\BreakReminder
python main.py
```

### "Sound doesn't play"
```bash
# Check volume
sndvol.exe

# Reinstall pygame
pip uninstall pygame -y
pip install pygame --force-reinstall
```

## Performance Monitoring

### Check running Python processes
```bash
tasklist | findstr python
```

### Kill Python process (if needed)
```bash
taskkill /IM python.exe /F
```

### Monitor system tray
- Right-click taskbar → Taskbar settings → Show hidden icons
- Look for "Break Reminder" or "B" icon

---

## Reference

**Project Location:** `C:\Users\suprunov-a\Documents\MaProjects\Claude\TimeToPauseApp\`

**Config Location:** `%APPDATA%\BreakReminder\`

**Dependencies:** pystray, pygame, pillow

**Python Version:** 3.9+

**Platform:** Windows 7+

---

**TIP:** Bookmark this file for quick reference during development!
