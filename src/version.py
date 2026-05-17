"""Version management for the app"""

APP_VERSION = "1.0.0"
GITHUB_REPO = "alexagnestor-wq/timetopause"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def parse_version(version_string: str) -> tuple:
    """Parse version string like '1.0.0' to (1, 0, 0)"""
    try:
        parts = version_string.strip('v').split('.')
        return tuple(int(p) for p in parts)
    except:
        return (0, 0, 0)

def is_update_available(latest_version: str) -> bool:
    """Check if latest_version is newer than APP_VERSION"""
    current = parse_version(APP_VERSION)
    latest = parse_version(latest_version)
    return latest > current
