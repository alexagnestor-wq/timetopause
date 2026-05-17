# Release & Update Guide

This guide explains how to create releases on GitHub so customers can automatically update sounds.

## How It Works

1. You create a GitHub Release with new sounds
2. App automatically detects the new release
3. User sees "Update Available" dialog
4. User clicks "Update" 
5. App downloads and extracts new sounds
6. App restarts with new sounds available

## Creating a Release

### Step 1: Update Version in Code

Edit `src/version.py`:
```python
APP_VERSION = "1.0.1"  # Increment version
```

### Step 2: Prepare Sounds

1. Create a folder with your new sound files:
   ```
   sounds/
   ├── alert.wav
   ├── beep.wav
   ├── chime.wav
   └── ...
   ```

2. Compress to `sounds.zip`:
   - Windows: Right-click folder → Send to → Compressed (zipped) folder
   - Mac: Right-click folder → Compress
   - Linux: `zip -r sounds.zip sounds/`

### Step 3: Create GitHub Release

1. Go to https://github.com/alexagnestor-wq/timetopause/releases
2. Click "Draft a new release"
3. **Tag version**: Enter version number (e.g., `v1.0.1`)
   - Must match the version in `src/version.py`
   - Use format: `vX.Y.Z`
4. **Release title**: "Version 1.0.1 - New Sounds"
5. **Description**: Describe what's new:
   ```
   ## New Sounds Added
   - alert.wav - New alert notification
   - beep.wav - Short beep
   - chime.wav - Gentle chime
   
   ## Updates
   - Fixed threading issues
   - Improved audio handling
   ```

### Step 4: Attach Sounds

1. Under "Attach binaries by dropping them here", upload:
   - `sounds.zip` - **MUST be named exactly this**
2. Make sure it's attached as an asset

### Step 5: Publish Release

1. Click "Publish release"
2. Done! Customers will be notified on next app startup

## Example Release

**Tag**: `v1.0.1`
**Title**: Version 1.0.1 - New Sounds
**Assets**:
- `sounds.zip` (contains your sound files)

## Testing Locally

To test the update system:

1. Change `APP_VERSION` in `src/version.py` to an older version (e.g., "0.9.0")
2. Run the app
3. It should detect the latest release as an update
4. Click "Update" to test the download flow

## Important Notes

- ⚠️ Sound file must be named **exactly** `sounds.zip`
- ⚠️ Version tag must be in format `vX.Y.Z` (e.g., `v1.0.1`)
- ⚠️ Version in tag must match `APP_VERSION` in code
- ✅ App checks GitHub API every time it starts
- ✅ User chooses when to update (not forced)
- ✅ Sounds extract automatically to `assets/sounds/`

## What Gets Updated

When user clicks "Update":
- ✅ New sounds are downloaded and installed
- ❌ App version doesn't change (auto-update coming soon)
- ❌ Other app code doesn't update (manual update needed)

Future enhancement: Auto-update entire app + version number.

## Troubleshooting

**"Update not detected?"**
- Check GitHub API isn't rate-limited (60 requests/hour for anonymous)
- Verify version tag format is `vX.Y.Z`
- Check console output for "UPDATE" messages

**"Sounds didn't extract?"**
- Ensure `sounds.zip` is valid and contains sound files
- Check assets/sounds/ folder has write permissions

**"Download failed?"**
- Check internet connection
- Verify sounds.zip is attached to release
- Check file size isn't too large
