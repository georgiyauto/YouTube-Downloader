import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os
import subprocess
from pathlib import Path

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("600x500")
        
        # Переменные
        self.url_var = tk.StringVar()
        self.quality_var = tk.StringVar()
        self.download_audio_var = tk.BooleanVar(value=True)
        self.download_video_var = tk.BooleanVar(value=True)
        self.available_formats = []
        self.download_thread = None
        self.ydl_instance = None
        self.is_downloading = False
        
        # Создаем интерфейс
        self.create_widgets()
        
    def create_widgets(self):
        # URL ввод
        url_frame = ttk.Frame(self.root, padding="10")
        url_frame.pack(fill=tk.X)
        
        ttk.Label(url_frame, text="URL видео:").pack(anchor=tk.W)
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=70)
        url_entry.pack(fill=tk.X, pady=5)
        
        # Кнопка получения форматов
        ttk.Button(url_frame, text="Получить доступные качества", 
                  command=self.get_formats).pack(pady=5)
        
        # Выбор качества
        quality_frame = ttk.Frame(self.root, padding="10")
        quality_frame.pack(fill=tk.X)
        
        ttk.Label(quality_frame, text="Качество:").pack(anchor=tk.W)
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var, 
                                          state="readonly", width=50)
        self.quality_combo.pack(fill=tk.X, pady=5)
        
        # Кнопки быстрого выбора
        quick_select_frame = ttk.Frame(self.root, padding="10")
        quick_select_frame.pack(fill=tk.X)
        
        ttk.Label(quick_select_frame, text="Быстрый выбор:").pack(anchor=tk.W)
        quick_buttons_frame = ttk.Frame(quick_select_frame)
        quick_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(quick_buttons_frame, text="Только видео", 
                  command=self.select_video_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_buttons_frame, text="Только аудио", 
                  command=self.select_audio_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_buttons_frame, text="Видео + аудио", 
                  command=self.select_video_audio).pack(side=tk.LEFT, padx=5)
        
        # Галочки для аудио и видео
        options_frame = ttk.Frame(self.root, padding="10")
        options_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(options_frame, text="Скачать видео", 
                       variable=self.download_video_var).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Скачать аудио", 
                       variable=self.download_audio_var).pack(anchor=tk.W)
        
        # Progress bar
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X)
        
        ttk.Label(progress_frame, text="Прогресс:").pack(anchor=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=580)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Готов к работе")
        self.status_label.pack(anchor=tk.W)
        
        # Кнопки управления
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.download_button = ttk.Button(button_frame, text="Скачать", 
                                        command=self.start_download)
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Стоп", 
                                     command=self.stop_download, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Открыть папку загрузок", 
                  command=self.open_download_folder).pack(side=tk.LEFT, padx=5)
        
    def get_formats(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL видео")
            return
            
        self.status_label.config(text="Получение форматов...")
        
        def get_formats_thread():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Получаем форматы видео
                    formats = []
                    if 'formats' in info:
                        for f in info['formats']:
                            if f.get('vcodec') != 'none' and f.get('height'):
                                quality = f"{f['height']}p"
                                if f.get('fps'):
                                    quality += f" {f['fps']}fps"
                                if f.get('ext'):
                                    quality += f" ({f['ext']})"
                                formats.append((quality, f['format_id']))
                    
                    # Добавляем опцию "лучшее качество"
                    formats.insert(0, ("Лучшее качество", "best"))
                    
                    self.available_formats = formats
                    
                    # Обновляем комбобокс в главном потоке
                    self.root.after(0, self.update_quality_combo, formats)
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Не удалось получить форматы: {str(e)}"))
                self.root.after(0, lambda: self.status_label.config(text="Ошибка получения форматов"))
        
        threading.Thread(target=get_formats_thread, daemon=True).start()
    
    def update_quality_combo(self, formats):
        self.quality_combo['values'] = [f[0] for f in formats]
        if formats:
            self.quality_combo.current(0)
        self.status_label.config(text="Форматы получены")
    
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL видео")
            return
            
        if not self.download_video_var.get() and not self.download_audio_var.get():
            messagebox.showerror("Ошибка", "Выберите хотя бы что-то одно: видео или аудио")
            return
            
        # Блокируем кнопки на время скачивания
        self.is_downloading = True
        self.download_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="Начало скачивания...")
        self.progress_var.set(0)
        
        def download_thread():
            try:
                # Определяем формат
                format_string = self.get_format_string()
                
                # Создаем папку для загрузок
                download_dir = Path.home() / "Downloads" / "YouTube Downloads"
                download_dir.mkdir(exist_ok=True)
                
                ydl_opts = {
                    'format': format_string,
                    'merge_output_format': 'mp4',
                    'outtmpl': str(download_dir / '%(title)s.%(ext)s'),
                    'continuedl': True,
                    'retries': 50,
                    'fragment_retries': 50,
                    'sleep_interval': 3,
                    'max_sleep_interval': 8,
                    'concurrent_fragment_downloads': 8,
                    'ignoreerrors': True,
                    'keepvideo': False,
                    'http_chunk_size': 10485760,
                    'quiet': True,
                    'no_warnings': True,
                    'progress_hooks': [self.progress_hook],
                }
                
                self.ydl_instance = yt_dlp.YoutubeDL(ydl_opts)
                with self.ydl_instance as ydl:
                    ydl.download([url])
                
                self.root.after(0, self.download_complete, str(download_dir))
                
            except Exception as e:
                if self.is_downloading:  # Только если не было остановки
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка скачивания: {str(e)}"))
                    self.root.after(0, lambda: self.status_label.config(text="Ошибка скачивания"))
            finally:
                self.is_downloading = False
                self.ydl_instance = None
                self.root.after(0, self.enable_buttons)
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def get_format_string(self):
        selected_quality = self.quality_var.get()
        format_id = None
        
        for quality, fid in self.available_formats:
            if quality == selected_quality:
                format_id = fid
                break
        
        if format_id == "best":
            if self.download_video_var.get() and self.download_audio_var.get():
                return 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
            elif self.download_video_var.get():
                return 'bestvideo[ext=mp4]/best'
            else:
                return 'bestaudio[ext=m4a]/best'
        else:
            if self.download_video_var.get() and self.download_audio_var.get():
                return f'{format_id}+bestaudio[ext=m4a]/best'
            elif self.download_video_var.get():
                return f'{format_id}/best'
            else:
                return 'bestaudio[ext=m4a]/best'
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            
            if total_bytes > 0:
                percent = (downloaded_bytes / total_bytes) * 100
                self.root.after(0, lambda p=percent: self.progress_var.set(p))
                
                speed = d.get('speed', 0)
                if speed:
                    speed_str = f"{speed/1024/1024:.1f} MB/s"
                else:
                    speed_str = "N/A"
                
                status_text = f"Скачано: {downloaded_bytes/1024/1024:.1f} MB / {total_bytes/1024/1024:.1f} MB ({percent:.1f}%) - {speed_str}"
                self.root.after(0, lambda: self.status_label.config(text=status_text))
                
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_label.config(text="Завершено! Обработка файла..."))
    
    def download_complete(self, download_dir):
        self.progress_var.set(100)
        self.status_label.config(text="Скачивание завершено!")
        self.enable_buttons()
        
        result = messagebox.askyesno("Завершено", 
                                     f"Скачивание завершено!\n\nОткрыть папку с загрузками?")
        if result:
            self.open_download_folder(download_dir)
    
    def stop_download(self):
        if self.is_downloading:
            self.is_downloading = False
            self.status_label.config(text="Остановка скачивания...")
            
            # Останавливаем yt-dlp
            if self.ydl_instance:
                try:
                    self.ydl_instance.params['noplaylist'] = True
                    # Принудительно останавливаем
                    import sys
                    sys.exit(1)
                except:
                    pass
            
            # Удаляем временные файлы
            self.cleanup_temp_files()
            
            # Возвращаем кнопки в рабочее состояние
            self.enable_buttons()
            self.progress_var.set(0)
            self.status_label.config(text="Скачивание отменено")
    
    def cleanup_temp_files(self):
        try:
            download_dir = Path.home() / "Downloads" / "YouTube Downloads"
            if download_dir.exists():
                # Удаляем временные файлы .part и .ytdl
                for file in download_dir.glob("*.part"):
                    file.unlink()
                for file in download_dir.glob("*.ytdl"):
                    file.unlink()
                for file in download_dir.glob("*.temp"):
                    file.unlink()
        except Exception as e:
            print(f"Ошибка при очистке временных файлов: {e}")
    
    def enable_buttons(self):
        self.download_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def select_video_only(self):
        self.download_video_var.set(True)
        self.download_audio_var.set(False)
    
    def select_audio_only(self):
        self.download_video_var.set(False)
        self.download_audio_var.set(True)
    
    def select_video_audio(self):
        self.download_video_var.set(True)
        self.download_audio_var.set(True)
    
    def open_download_folder(self, path=None):
        if path is None:
            path = Path.home() / "Downloads" / "YouTube Downloads"
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(path)
            elif os.name == 'posix':  # macOS и Linux
                subprocess.run(['open', path], check=True)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
