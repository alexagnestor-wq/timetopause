# Adding Custom Sounds - Step by Step

## Quick Version (TL;DR)

1. Get a `.wav` file
2. Copy to: `%APPDATA%\BreakReminder\assets\sounds\myalert.wav`
3. Restart app
4. Bonus: Edit `src/notifications.py` line with `sound_filename=...` to use your file

---

## Detailed Guide

### Step 1: Prepare Your Sound File

#### Option A: Find a Pre-made Sound
- **Freesound.org** - https://freesound.org/
  - Search for "alert", "beep", "notification"
  - Download as WAV
  - Free account needed

- **Zapsplat** - https://www.zapsplat.com/
  - Search "alert sounds"
  - Download as WAV
  - No account needed

- **YouTube to Audio Converter**
  - https://ytmp3.cc/
  - Convert YouTube sound → download as WAV

#### Option B: Create Your Own Sound
- **Online Tone Generator** - https://www.szynalski.com/tone-generator/
  1. Set frequency (e.g., 1000 Hz for standard beep)
  2. Set duration (e.g., 2 seconds)
  3. Click "Generate"
  4. Download as WAV
  5. Optional: Edit in Audacity to add variation

- **Audacity** (free software) - https://www.audacityteam.org/
  1. Download & install
  2. Generate tone: Generate → Tones → pick frequency
  3. Add effects: Echo, Fade in/out, etc.
  4. Export as WAV

### Step 2: Verify Your Sound File

**Format Required:** WAV (`.wav` extension)

**Recommended Specs:**
- Sample rate: 44100 Hz (standard)
- Channels: Mono or Stereo (both work)
- Bit depth: 16-bit
- Duration: 0.5 - 3 seconds
- File size: < 1 MB

**Check in Windows:**
- Right-click file → Properties
- Should show "Audio file" or "WAVE Audio"
- Duration should be reasonable

### Step 3: Copy Sound to App Folder

#### Method 1: Via Windows Explorer (Easiest)

1. Open Windows Explorer
2. Type in address bar: `%APPDATA%\BreakReminder`
   (Windows will auto-navigate there)

3. Open `assets` folder
4. Open `sounds` folder
5. Paste your `.wav` file here

**Result:**
```
%APPDATA%\BreakReminder\assets\sounds\
├── myalert.wav          ← Your custom sound
└── (other sounds)
```

#### Method 2: Via Command Line

```bash
# Copy to sounds folder
copy "C:\path\to\your\alert.wav" "%APPDATA%\BreakReminder\assets\sounds\"

# Verify it's there
dir "%APPDATA%\BreakReminder\assets\sounds\"
```

#### Method 3: Via PowerShell

```powershell
$source = "C:\path\to\your\alert.wav"
$dest = "$env:APPDATA\BreakReminder\assets\sounds\"
Copy-Item $source $dest
Get-ChildItem $dest
```

### Step 4: Test the Sound

#### Quick Test (in Python)
```bash
python -c "
from src.notifications import NotificationManager
from pathlib import Path
nm = NotificationManager(Path.home() / 'AppData' / 'Roaming' / 'BreakReminder')
nm.play_sound('myalert.wav')
"
```

#### Or Use Test Script
```bash
python test_components.py
```
This tests all sounds available in the folder.

### Step 5: Use Your Sound in App (Optional)

**Option 1: Make it the Default**
Edit `src/notifications.py`:

Find this line (around line 75):
```python
def notify(self, notification_type: str = "mixed", sound_filename: Optional[str] = None, volume: int = 100):
```

And in the same file, change line where sound is played:
```python
# Change from:
self.play_sound(sound_filename, volume)

# To:
self.play_sound("myalert.wav", volume)  # Your custom sound
```

**Option 2: Use from Settings (Future Feature)**
Currently, the app uses `default.wav` or falls back to system beep.

To implement custom sound selection (Phase 2):
1. Add dropdown in `src/ui.py` settings window
2. List all `.wav` files from sounds folder
3. Save selection to config.json
4. Load from config in `_on_reminder()`

### Step 6: Restart App

```bash
python main.py
```

Now when a reminder triggers, it will play your custom sound!

---

## Sound File Recommendations

### Good Alerts
- **Simple beep**: 800-1200 Hz, 0.5 seconds
- **Chime**: More musical, 1-2 seconds
- **Melodic alert**: 2-3 seconds duration
- **Ascending tone**: Starts low, goes high (gets attention)

### Too Harsh
- ❌ Screeching sounds (>3000 Hz)
- ❌ Very loud volumes (normalize to -6dB in Audacity)
- ❌ Very long sounds (>5 seconds)
- ❌ Multiple overlapping tones (confusing)

### Perfect Range
- ✅ 800-2000 Hz (pleasant range for humans)
- ✅ 1-2 seconds (attention without annoyance)
- ✅ -6dB to -3dB (loud but not distorted)
- ✅ Fade in/out (smooth, professional)

---

## Creating a Custom Sound in Audacity

### Simple Beep (2 minutes)

1. **Open Audacity** (free audio editor)
2. **Generate tone:**
   - Menu: Generate → Tone Generator
   - Frequency: 1000 Hz
   - Amplitude: 0.8
   - Duration: 1.5 seconds
   - Click Generate

3. **Add fade in/out:**
   - Select all (Ctrl+A)
   - Menu: Effect → Fade In
   - Menu: Effect → Fade Out

4. **Export:**
   - File → Export → Export as WAV
   - Name: `myalert.wav`
   - Click Export
   - Keep default settings, click Export again

5. **Done!** Now copy to `%APPDATA%\BreakReminder\assets\sounds\`

### Notification Chime (3 minutes)

1. **Generate first tone:**
   - Generate → Tone Generator
   - Frequency: 800 Hz
   - Duration: 0.5 seconds
   - Click Generate

2. **Append second tone:**
   - End of track → Generate → Tone Generator
   - Frequency: 1200 Hz
   - Duration: 0.5 seconds
   - Click Generate

3. **Result:** Two-tone alert (professional sounding)

4. **Export as WAV** as above

---

## Multiple Sounds (Future Feature)

Once you have several sounds, the Phase 2 asset system will let users:
1. Rotate through different sounds
2. Have weekend vs weekday sounds
3. Have gradually-increasing alert intensity
4. Community-shared sound library

For now, you can manually test different sounds by:
1. Renaming current sound
2. Copying new one to same folder
3. Restarting app

---

## Troubleshooting

### Sound doesn't play

**Problem:** I added sound but nothing plays

**Solutions:**
1. Check if file is actually in `%APPDATA%\BreakReminder\assets\sounds\`
2. Verify filename is exactly correct (case-sensitive)
3. Run test: `python test_components.py` → check "Testing sound"
4. Check Windows volume (not muted)
5. Verify pygame installed: `pip install pygame --upgrade`

### Sound plays but volume is wrong

**Problem:** Too loud or too quiet

**Solution 1 - Edit in Audacity:**
1. Open sound in Audacity
2. Select all (Ctrl+A)
3. Effect → Normalize → Click Normalize
4. File → Export as WAV

**Solution 2 - Change volume in app:**
Edit `src/settings.py`:
```python
@dataclass
class Config:
    volume: int = 100  # Change to 50 for quieter, 150 for louder
```

### File is corrupt

**Problem:** "Error opening audio file"

**Solution:**
1. Verify it's a valid WAV file
2. Open in Audacity to check
3. Re-export from Audacity as WAV
4. Check file size (should be > 1 KB)

### Can't find the sounds folder

**Problem:** `%APPDATA%\BreakReminder` doesn't exist

**Solution:**
1. Run app once: `python main.py`
2. Folder will be created automatically
3. Then add your sounds

---

## Sound Libraries (Recommendations)

### Free Sounds Websites
| Site | License | Best For |
|------|---------|----------|
| Freesound.org | Various | High quality, curated |
| Zapsplat.com | Free | Alert sounds, FX |
| Pixabay | CC0 | Royalty-free |
| Opengameart.org | CC | Game-like sounds |

### Tools
| Tool | Type | Best For |
|------|------|----------|
| Audacity | Editor | Create & edit |
| Tone Generator | Generator | Simple beeps |
| FL Studio | DAW | Professional |
| GarageBand (Mac) | DAW | Quick sounds |

---

## Phase 2: Asset Library (GitHub)

In the future, the app will support:

```json
{
  "version": "1.0.0",
  "sounds": [
    {
      "name": "alert_beep.wav",
      "url": "https://github.com/yourusername/break-reminder-assets/raw/main/sounds/alert_beep.wav",
      "hash": "abc123...",
      "category": "beep"
    },
    {
      "name": "chime_musical.wav",
      "url": "...",
      "hash": "def456...",
      "category": "chime"
    }
  ]
}
```

Users will be able to:
- Browse available sounds in app
- Preview before downloading
- Auto-download updates
- Vote on favorites

---

## Summary

**Current (MVP):**
1. Drop `.wav` files in `%APPDATA%\BreakReminder\assets\sounds\`
2. Restart app
3. App uses them automatically (or falls back to system beep)

**Recommended Workflow:**
1. Find sound on Freesound.org or create in Audacity
2. Download/export as WAV
3. Copy to sounds folder
4. Test with app
5. Adjust if needed (volume, duration)

**Next Phase:**
- GitHub-based asset management
- Auto-updates for sound library
- User interface for sound selection
- Community contributions

---

Happy sound customizing! 🎵
