## Installation:
- git clone the repository
- use docker-compose to build and run the container

```
use crontab -e to start docker container every x minutes:
{{CRON EXPRESSION}} docker compose -f /path/to/docker-compose.yml up -d
```

## Configurations:

Create .env file in root directory to set environment variables or set in docker-compose.yml file:

```
GEMINI_API_KEY=your_gemini_api_key
```

In docker-compose.yml file, set the volume to the directory you want to watch:

```
volumes:
  - /path/to/watch/folder:/app/watchlist/folder_name

Example:

volumes:
  - /downloads/tvshows:/app/watchlist/tvshows
```

Other configurations can be set in the docker-compose.yml environment as well:

```
  - WATCH_EXTENSION=.mp4;.mkv;.avi;.nfo;.srt
  - EXCLUDE_FILE=tvshow.nfo;season.nfo
```

Check gemini's api for free tier limitation (usually 1500 requests per day), one watched directory is one request
