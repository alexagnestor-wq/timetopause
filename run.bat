@echo off
REM Time to Pause - Quick Start Script

REM Переходим в папку приложения
cd /d "%~dp0"

REM Запускаем приложение БЕЗ видимого окна консоли
start "" pythonw.exe main.py

REM Закрываем консоль
exit /b 0
