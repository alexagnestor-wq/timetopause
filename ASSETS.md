# Asset Management Guide

## Overview

Break Reminder поддерживает пользовательские звуки и визуальные эффекты. Система позволяет обновлять библиотеку без переустановки приложения.

## Current Implementation (MVP)

Звуки хранятся локально в:
```
%APPDATA%\BreakReminder\assets\sounds\
```

Если звуковой файл не найден, приложение использует системный beep.

## Future: GitHub-Based Asset Management

### Структура репозитория (планируется)

```
break-reminder-assets/
├── sounds/
│   ├── alert_1.wav       # 1 second beep
│   ├── alert_2.wav       # Different tone
│   ├── chime_1.wav       # Notification chime
│   └── ...
├── visuals/
│   ├── flash_bright.json  # Full brightness flash
│   ├── flash_soft.json    # Dimmed flash
│   └── ...
└── manifest.json          # Version info & file list
```

### manifest.json Example

```json
{
  "version": "1.0.0",
  "sounds": [
    {
      "name": "alert_1.wav",
      "url": "https://raw.githubusercontent.com/yourusername/break-reminder-assets/main/sounds/alert_1.wav",
      "hash": "abc123...",
      "size": 50000
    },
    {
      "name": "chime_1.wav",
      "url": "...",
      "hash": "def456...",
      "size": 35000
    }
  ],
  "visuals": [...]
}
```

### How Auto-Update Would Work

1. **On app startup:**
   ```python
   # Check if assets are up to date
   local_manifest = load_local_manifest()
   remote_manifest = fetch_github_manifest()
   
   if remote_manifest.version > local_manifest.version:
       download_new_assets()
       update_local_manifest()
   ```

2. **On user demand:**
   - Add "Check for Updates" button in Settings
   - Manual refresh of asset library

3. **Safety:**
   - Verify file hashes (SHA256)
   - Keep local backup of old assets
   - Rollback if corrupted

## Adding Sounds (Current MVP)

### Step 1: Create/Find Sound Files
- Format: **.wav** (mono or stereo)
- Sample rate: 44100 Hz (standard)
- Duration: 0.5 - 3 seconds (recommended)
- Size: < 1 MB

### Step 2: Place in Assets Folder
```
%APPDATA%\BreakReminder\assets\sounds\alert_my_custom.wav
```

### Step 3: Use in Code (Advanced)
Edit `src/notifications.py`:
```python
def _on_reminder(self):
    self.notification_manager.notify(
        notification_type="sound",
        sound_filename="alert_my_custom.wav",  # Your custom file
        volume=100
    )
```

## Recommended Tools

### Sound Editing
- **Audacity** (free, open-source) - https://www.audacityteam.org/
- **Freesound** (free sound library) - https://freesound.org/
- **Zapsplat** (free sound effects) - https://www.zapsplat.com/

### Creating Sounds
- Beep tone generator: https://www.szynalski.com/tone-generator/
- Convert to WAV: FFmpeg or online tools

## Adding Visual Effects (Future)

### Flash Styles (JSON)
```json
{
  "name": "flash_bright",
  "description": "Full brightness white flash",
  "backgroundColor": "#FFFFFF",
  "textColor": "#000000",
  "duration": 3.0,
  "opacity": 1.0,
  "animation": "instant"
}
```

### Implement in Code
Edit `src/notifications.py`:
```python
def show_flash(self, style: str = "bright"):
    visual_config = load_visual_config(style)
    # Use config to customize appearance
```

## Best Practices

1. **Keep assets small** - Users on slow internet benefit
2. **Use standard formats** - WAV for audio, JSON for configs
3. **Version everything** - Manifest + hash checking
4. **Test thoroughly** - Different Windows versions, audio devices
5. **Gather feedback** - Let users suggest sounds/effects

## Migration Path

### Phase 1 (Current MVP)
- ✅ Local sounds only
- ✅ Hardcoded visuals

### Phase 2 (Soon)
- 🚧 GitHub manifest system
- 🚧 Auto-download on startup

### Phase 3 (Later)
- 🚧 User-created sounds
- 🚧 Voting/rating system
- 🚧 CDN caching

## Questions?

Need help setting up custom assets? Check:
1. `README.md` - General setup
2. `src/notifications.py` - How assets are loaded
3. `%APPDATA%\BreakReminder\config.json` - User settings
