# YT_Vid_Downloader

A fully-featured YouTube video downloader application built with Python and yt-dlp. This application allows you to download YouTube videos in various formats and qualities with a user-friendly interface.

## Features

- Download YouTube videos in multiple formats and resolutions
- Extract audio as MP3
- Track download progress with a progress bar
- Choose your download location
- Available in both GUI and CLI modes
- Detailed logging of download progress

## Requirements

- Python 3.6 or higher
- yt-dlp
- tkinter (included with most Python installations)
- FFmpeg (required for audio extraction and some video formats)
  - Download from: https://ffmpeg.org/download.html
  - Make sure to add it to your system PATH

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

### GUI Mode (Default)

To run the application with a graphical user interface:

```
python youtube_downloader.py
```

### CLI Mode

To run the application in command-line interface mode:

```
python youtube_downloader.py --cli
```

## How to Use

1. Enter a valid YouTube URL
2. Select your preferred format/quality
3. Choose a download location (or use the default)
4. Click the "Download" button
5. Monitor the progress in the progress bar and log area

## Available Download Formats

- Best Video + Audio (highest quality available)
- Best Audio Only (MP3)
- 1080p MP4
- 720p MP4
- 480p MP4

## Notes

- The application requires an active internet connection
- Download speeds depend on your internet connection and YouTube's server load
- Some videos may not be available in all formats due to YouTube restrictions
