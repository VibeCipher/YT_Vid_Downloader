import os
import sys
import tkinter as tk
import threading
from tkinter import ttk, filedialog, messagebox
import yt_dlp

class YoutubeDownloader:
    def __init__(self):
        self.output_path = os.path.join(os.path.expanduser("~"), "Downloads")
        self.formats = {
            "Best Video + Audio": "best",
            "Best Audio Only (MP3)": "bestaudio/best",
            "720p MP4": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]",
            "1080p MP4": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]",
            "480p MP4": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]"
        }
        
    def download_video(self, url, format_option, output_path=None, progress_callback=None):
        if not url:
            raise ValueError("URL cannot be empty")
            
        if output_path:
            self.output_path = output_path
            
        format_code = self.formats.get(format_option, "best")
        
        ydl_opts = {
            'format': format_code,
            'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'ignoreerrors': False,  # Don't ignore errors
            'verbose': True,        # More verbose output for debugging
        }
        
        # If audio only is selected, convert to mp3
        if format_option == "Best Audio Only (MP3)":
            # Check if FFmpeg is available for audio extraction
            if not check_ffmpeg():
                return {
                    'status': 'error',
                    'error': "FFmpeg is required for audio extraction. Please install FFmpeg and add it to your PATH."
                }
                
            ydl_opts.update({
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        
        # Add progress hook if callback is provided
        if progress_callback:
            ydl_opts['progress_hooks'] = [progress_callback]
            
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # First check if the video is available in the requested format
                info_dict = ydl.extract_info(url, download=False)
                
                # Now download the video
                info = ydl.extract_info(url, download=True)
                return {
                    'status': 'success',
                    'title': info.get('title', 'Unknown'),
                    'filename': ydl.prepare_filename(info),
                    'path': self.output_path,
                    'format': format_option
                }
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower() or "postprocessor" in error_msg.lower():
                return {
                    'status': 'error',
                    'error': f"FFmpeg error: {error_msg}\nPlease install FFmpeg from https://ffmpeg.org/download.html"
                }
            else:
                return {
                    'status': 'error',
                    'error': f"Download error: {error_msg}"
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }


class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        
        self.downloader = YoutubeDownloader()
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL input
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Format selection
        ttk.Label(main_frame, text="Format:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value=list(self.downloader.formats.keys())[0])
        ttk.Combobox(main_frame, textvariable=self.format_var, values=list(self.downloader.formats.keys()), state="readonly").grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Output path
        ttk.Label(main_frame, text="Save to:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.path_var = tk.StringVar(value=self.downloader.output_path)
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_path).grid(row=2, column=2, padx=5, pady=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Progress:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Download button
        ttk.Button(main_frame, text="Download", command=self.start_download).grid(row=5, column=1, pady=10)
        
        # Log area
        ttk.Label(main_frame, text="Log:").grid(row=6, column=0, sticky=tk.NW, pady=5)
        self.log_text = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD)
        self.log_text.grid(row=6, column=1, columnspan=2, sticky=tk.NSEW, pady=5)
        scrollbar = ttk.Scrollbar(main_frame, command=self.log_text.yview)
        scrollbar.grid(row=6, column=3, sticky=tk.NS)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
    def browse_output_path(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            # Calculate progress percentage
            if 'total_bytes' in d and d['total_bytes'] > 0:
                percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                self.progress_var.set(percent)
                
                # Update status with download speed and ETA
                if 'speed' in d and d['speed'] is not None:
                    speed_mb = d['speed'] / 1024 / 1024  # Convert to MB/s
                    eta = d.get('eta', 'Unknown')
                    status = f"Downloading: {percent:.1f}% @ {speed_mb:.2f} MB/s, ETA: {eta} seconds"
                    self.status_var.set(status)
                    
            # Log download progress
            if '_percent_str' in d and '_speed_str' in d and '_eta_str' in d:
                self.log_message(f"Progress: {d['_percent_str']}, Speed: {d['_speed_str']}, ETA: {d['_eta_str']}")
                
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.status_var.set("Download complete! Processing file...")
            self.log_message(f"Download complete: {d['filename']}")
            
    def start_download(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting download...")
        self.log_message(f"Starting download of: {url}")
        
        # Start download in a separate thread
        threading.Thread(
            target=self.download_thread,
            args=(url, self.format_var.get(), self.path_var.get()),
            daemon=True
        ).start()
        
    def download_thread(self, url, format_option, output_path):
        try:
            result = self.downloader.download_video(
                url, format_option, output_path, self.progress_hook
            )
            
            if result['status'] == 'success':
                self.root.after(0, lambda: self.status_var.set(f"Download complete: {result['title']}"))
                self.root.after(0, lambda: self.log_message(f"Successfully downloaded: {result['title']}"))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Download complete!\n\nTitle: {result['title']}\nSaved to: {result['path']}"))
            else:
                self.root.after(0, lambda: self.status_var.set(f"Error: {result['error']}"))
                self.root.after(0, lambda: self.log_message(f"Error: {result['error']}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {result['error']}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            self.root.after(0, lambda: self.log_message(f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}"))


def run_gui():
    root = tk.Tk()
    app = DownloaderGUI(root)
    root.mainloop()


def run_cli():
    downloader = YoutubeDownloader()
    
    # Print header
    print("\n===== YouTube Video Downloader (CLI) =====\n")
    
    # Get URL
    url = input("Enter YouTube URL: ").strip()
    if not url:
        print("Error: URL cannot be empty")
        return
        
    # Show format options
    print("\nAvailable formats:")
    formats = list(downloader.formats.keys())
    for i, fmt in enumerate(formats, 1):
        print(f"{i}. {fmt}")
        
    # Get format choice
    try:
        choice = int(input("\nSelect format (number): "))
        if choice < 1 or choice > len(formats):
            raise ValueError()
        format_option = formats[choice-1]
    except (ValueError, IndexError):
        print("Invalid choice. Using default format.")
        format_option = formats[0]
        
    # Get output path (optional)
    custom_path = input(f"\nOutput directory (default: {downloader.output_path}): ").strip()
    output_path = custom_path if custom_path else None
    
    # Progress callback for CLI
    def cli_progress_hook(d):
        if d['status'] == 'downloading':
            if '_percent_str' in d and '_speed_str' in d and '_eta_str' in d:
                sys.stdout.write(f"\rProgress: {d['_percent_str']}, Speed: {d['_speed_str']}, ETA: {d['_eta_str']}")
                sys.stdout.flush()
        elif d['status'] == 'finished':
            print(f"\nDownload complete: {d['filename']}")
            print("Processing file...")
    
    # Start download
    print(f"\nDownloading {url} in {format_option} format...")
    result = downloader.download_video(url, format_option, output_path, cli_progress_hook)
    
    # Show result
    if result['status'] == 'success':
        print(f"\nDownload successful!")
        print(f"Title: {result['title']}")
        print(f"Saved to: {result['path']}")
    else:
        print(f"\nDownload failed: {result['error']}")


def check_ffmpeg():
    """Check if FFmpeg is installed and available in PATH"""
    try:
        with yt_dlp.utils.Popen(['ffmpeg', '-version'], stdout=yt_dlp.utils.subprocess.PIPE, stderr=yt_dlp.utils.subprocess.PIPE) as proc:
            proc.communicate()
            return proc.returncode == 0
    except Exception:
        return False

if __name__ == "__main__":
    # Check if yt-dlp is installed
    try:
        import yt_dlp
    except ImportError:
        print("Error: yt-dlp is not installed. Please install it using:")
        print("pip install yt-dlp")
        sys.exit(1)
    
    # Check for FFmpeg
    if not check_ffmpeg():
        print("Warning: FFmpeg is not installed or not in PATH.")
        print("Some features like audio extraction and format conversion may not work.")
        print("Please install FFmpeg from https://ffmpeg.org/download.html")
        print("\nContinuing without FFmpeg...\n")
        
    # Determine whether to use GUI or CLI
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        run_cli()
    else:
        run_gui()