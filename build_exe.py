import PyInstaller.__main__
import os

# Путь к основному файлу
main_script = "youtube_downloader_gui.py"

# Параметры для PyInstaller
pyinstaller_args = [
    main_script,
    '--name=YouTubeDownloader',
    '--onefile',  # Создать один exe файл
    '--windowed',  # Без консольного окна (для GUI)
    '--clean',  # Очистить временные файлы
    '--noconfirm',  # Не запрашивать подтверждение
    '--distpath=dist',  # Путь для готового exe
    '--workpath=build',  # Путь для временных файлов
    '--specpath=.',  # Путь для spec файла
    '--add-data=*.ico;.' if os.path.exists('*.ico') else '',  # Добавить иконку если есть
    '--icon=icon.ico' if os.path.exists('icon.ico') else '',  # Иконка приложения
]

# Удаляем пустые аргументы
pyinstaller_args = [arg for arg in pyinstaller_args if arg]

print("Сборка exe файла...")
print(f"Команда: pyinstaller {' '.join(pyinstaller_args)}")

# Запускаем PyInstaller
PyInstaller.__main__.run(pyinstaller_args)

print("\nСборка завершена!")
print("exe файл находится в папке 'dist'")
