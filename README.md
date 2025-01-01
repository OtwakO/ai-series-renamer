use .env file in root directory to set environment variables or set in docker-compose.yml file:

```
GEMINI_API_KEY=your_gemini_api_key
```

In docker-compose.yml file:

-   set the volume to the directory you want to watch:
-   set the environment variables:
    -   WATCH_EXTENSION=.mp4;.mkv;.avi;.nfo;.srt #Seperate by ;
    -   EXCLUDE_FILE=tvshow.nfo;season.nfo #file names to ignore, seperate by ;

```
volumes:
  - /path/to/watch:/watch

e.g
volumes:
  - /downloads/tvshows:/watch/tvshows
```

```
use crontab -e to start docker container every x minutes:
{{CRON EXPRESSION}} docker compose -f /path/to/docker-compose.yml up -d
```

Check gemini's api for free tier limitation (usually 1500 requests per day), each watched directory is one request per x minutes.
