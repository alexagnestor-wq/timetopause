import pystray
from pystray import MenuItem
from PIL import Image, ImageDraw
import threading
from typing import Callable, Optional
from pathlib import Path

class TrayManager:
    """Управление иконкой в системном трее"""

    def __init__(
        self,
        icon_path: Optional[Path] = None,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_show: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_exit: Optional[Callable] = None,
    ):
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_show = on_show
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.icon: Optional[pystray.Icon] = None
        self.is_running = False

        # Загрузить иконку из assets
        if icon_path is None:
            icon_path = Path(__file__).parent.parent / "assets" / "icon.ico"

        if icon_path and icon_path.exists():
            try:
                self.image = Image.open(icon_path)
            except Exception as e:
                print(f"Could not load icon: {e}, using default")
                self.image = self._generate_default_icon()
        else:
            self.image = self._generate_default_icon()

    def _generate_default_icon(self) -> Image.Image:
        """Сгенерировать иконку по умолчанию (белый квадрат с буквой B)"""
        img = Image.new('RGB', (64, 64), color='#1f1f1f')  # Тёмный фон
        draw = ImageDraw.Draw(img)

        # Рисуем белый квадрат
        draw.rectangle([8, 8, 56, 56], fill='#00D4FF', outline='white', width=2)

        # Рисуем букву B
        draw.text((28, 24), "B", fill='white', font=None)

        return img

    def setup_menu(self):
        """Создать меню для трея"""
        menu = pystray.Menu(
            MenuItem("🪟 Show Window", self._menu_show),
            pystray.Menu.SEPARATOR,
            MenuItem("▶ Start", self._menu_start, default=False),
            MenuItem("⏸ Stop", self._menu_stop),
            pystray.Menu.SEPARATOR,
            MenuItem("⚙ Settings", self._menu_settings),
            MenuItem("❌ Exit", self._menu_exit),
        )
        return menu

    def _menu_show(self, icon, item):
        """Обработчик Show Window"""
        if self.on_show:
            self.on_show()

    def _menu_start(self, icon, item):
        """Обработчик Start"""
        if self.on_start:
            self.on_start()

    def _menu_stop(self, icon, item):
        """Обработчик Stop"""
        if self.on_stop:
            self.on_stop()

    def _menu_settings(self, icon, item):
        """Обработчик Settings"""
        if self.on_settings:
            self.on_settings()

    def _menu_exit(self, icon, item):
        """Обработчик Exit"""
        if self.on_exit:
            self.on_exit()
        icon.stop()

    def start(self):
        """Запустить приложение (запустить иконку в трее)"""
        if self.icon is not None:
            return

        self.is_running = True
        self.icon = pystray.Icon(
            "time-to-pause",
            self.image,
            title="Time to Pause",
            menu=self.setup_menu()
        )

        # НЕ запускаем таймер автоматически при инициализации трея
        # Таймер должен запускаться только когда пользователь нажимает START кнопку
        # if self.on_start:
        #     self.on_start()

        # Запустить в отдельном потоке, чтобы не блокировать UI
        threading.Thread(target=self.icon.run, daemon=True).start()

    def stop(self):
        """Остановить приложение"""
        self.is_running = False
        if self.on_stop:
            self.on_stop()

    def show_notification(self, title: str, message: str, duration: int = 5000):
        """Показать системное уведомление (Windows notification)"""
        # Windows notifications disabled due to compatibility issues
        # Приложение работает с системным трей иконкой
        pass

    def update_menu(self):
        """Обновить меню (например, для обновления текста Start/Stop)"""
        if self.icon:
            self.icon.menu = self.setup_menu()

    def quit(self):
        """Полностью завершить работу"""
        if self.icon:
            self.icon.stop()
        self.is_running = False
