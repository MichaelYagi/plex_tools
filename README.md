# Plex Open Subtitles Downloader

* Create an `.env` file
* It must contain:
```
# Plex Configuration
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your-plex-token-here

# OpenSubtitles Configuration
OPENSUBTITLES_API_KEY=your-api-key-here
OPENSUBTITLES_USERNAME=your-username
OPENSUBTITLES_PASSWORD=your-password

# Subtitle Languages (comma-separated, 2-letter codes)
SUBTITLE_LANGUAGES=en
```

## Usage guide:

### Download up to 10 subtitles
python plex_subtitle_downloader.py --library "Movies" --max-downloads 10

### Download up to 50 subtitles for all libraries
python plex_subtitle_downloader.py --max-downloads 50

### Download everything (no limit)
python plex_subtitle_downloader.py --library "Movies"

### Custom report filename
python plex_subtitle_downloader.py --max-downloads 20 --report my_report.txt

**Sample Report Output:**
```
================================================================================
SUBTITLE DOWNLOAD REPORT
================================================================================
Total subtitles downloaded: 15
Generated: 2026-01-17 14:30:22
================================================================================

MOVIES (10 subtitles)
--------------------------------------------------------------------------------

Inception
  Language: EN
  Rating: 8.5/10
  Downloads: 45,203
  Release: Inception.2010.1080p.BluRay.x264
  Uploader: john_doe
  File: Inception.en.srt
  Timestamp: 2026-01-17 14:25:10

...

TV EPISODES (5 subtitles)
--------------------------------------------------------------------------------

Breaking Bad - S01E01 - Pilot
  Language: EN
  Rating: 9.2/10
  Downloads: 12,450
  Release: Breaking.Bad.S01E01.1080p.WEB-DL
  Uploader: subtitle_master
  File: S01E01.en.srt
  Timestamp: 2026-01-17 14:28:33

...

================================================================================
SUMMARY STATISTICS
================================================================================
Average subtitle rating: 8.7/10
Total community downloads: 234,567

Language breakdown:
  EN: 15
================================================================================
```