"""GitHub auto-updater module"""

import json
import threading
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Callable

from src.version import GITHUB_API_URL, APP_VERSION, is_update_available


class UpdateChecker:
    """Check for updates from GitHub releases"""

    def __init__(self, on_update_available: Optional[Callable] = None):
        self.on_update_available = on_update_available
        self.latest_version = None
        self.download_url = None

    def check_for_updates(self):
        """Check GitHub API for new releases (runs in background thread)"""
        threading.Thread(target=self._check, daemon=True).start()

    def _check(self):
        """Internal check logic"""
        try:
            print("[UPDATE] Checking for updates...")

            with urllib.request.urlopen(GITHUB_API_URL, timeout=5) as response:
                data = json.loads(response.read().decode())

                if not data:
                    print("[UPDATE] No releases found")
                    return

                latest_version = data.get('tag_name', '')

                if is_update_available(latest_version):
                    self.latest_version = latest_version
                    print(f"[UPDATE] New version available: {latest_version}")

                    if self.on_update_available:
                        self.on_update_available(latest_version)
                else:
                    print(f"[UPDATE] App is up to date (current: {APP_VERSION})")

        except urllib.error.URLError as e:
            print(f"[UPDATE] Network error: {e}")
        except Exception as e:
            print(f"[UPDATE] Error checking updates: {e}")

    def get_release_info(self, version: str) -> dict:
        """Get release info from GitHub API"""
        try:
            url = f"https://api.github.com/repos/alexagnestor-wq/timetopause/releases/tags/{version}"
            with urllib.request.urlopen(url, timeout=5) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            print(f"[UPDATE] Error getting release info: {e}")
            return {}

    def download_release(self, version: str, download_dir: Path) -> bool:
        """Download release assets from GitHub"""
        try:
            print(f"[UPDATE] Downloading {version}...")

            release_info = self.get_release_info(version)
            if not release_info:
                print("[UPDATE] Could not fetch release info")
                return False

            assets = release_info.get('assets', [])
            download_dir.mkdir(parents=True, exist_ok=True)

            success = True
            for asset in assets:
                if asset['name'] == 'sounds.zip':
                    print(f"[UPDATE] Found sounds.zip in release")
                    asset_url = asset['browser_download_url']

                    # Download the file
                    zip_path = download_dir / 'sounds.zip'
                    print(f"[UPDATE] Downloading from: {asset_url}")

                    try:
                        urllib.request.urlretrieve(asset_url, zip_path)
                        print(f"[UPDATE] Downloaded to: {zip_path}")
                    except Exception as e:
                        print(f"[UPDATE] Download failed: {e}")
                        success = False

            if success and any(a['name'] == 'sounds.zip' for a in assets):
                return True
            else:
                print("[UPDATE] sounds.zip not found in release")
                return False

        except Exception as e:
            print(f"[UPDATE] Error downloading release: {e}")
            return False

    def extract_sounds(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract sounds.zip to assets/sounds directory"""
        try:
            import zipfile

            print(f"[UPDATE] Extracting sounds to {extract_to}...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            # Clean up zip
            zip_path.unlink()

            print("[UPDATE] Sounds extracted successfully")
            return True

        except Exception as e:
            print(f"[UPDATE] Error extracting sounds: {e}")
            return False
