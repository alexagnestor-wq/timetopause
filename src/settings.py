import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class Config:
    """Конфигурация приложения"""
    interval_minutes: float = 30  # в минутах (может быть дробь для секунд)
    notification_type: str = "mixed"  # "sound", "flash", "mixed"
    sound_enabled: bool = True
    flash_enabled: bool = True
    volume: int = 100  # 0-100
    keep_in_tray: bool = True
    calendar_alert_minutes: int = 10
    skipped_update_version: str = ""  # version the user chose to skip

class SettingsManager:
    def __init__(self):
        self.config_dir = Path(os.getenv('APPDATA')) / 'BreakReminder'
        self.config_file = self.config_dir / 'config.json'
        self.assets_dir = self.config_dir / 'assets'

        # Создаём папки если их нет
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        self.config = self._load_config()

    def _load_config(self) -> Config:
        """Загрузить конфиг из файла или создать новый"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return Config(**data)
            except Exception as e:
                print(f"Ошибка при загрузке конфига: {e}")
                return Config()
        return Config()

    def save_config(self):
        """Сохранить конфиг в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при сохранении конфига: {e}")

    def update_interval(self, minutes: float):
        """Обновить интервал напоминаний"""
        self.config.interval_minutes = float(minutes)
        self.save_config()

    def update_notification_type(self, notification_type: str):
        """Обновить тип уведомления"""
        if notification_type in ["sound", "flash", "mixed", "random"]:
            self.config.notification_type = notification_type
            self.save_config()

    def get_config(self) -> Config:
        """Получить текущий конфиг"""
        return self.config
