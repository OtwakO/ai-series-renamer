import os
import re
import time
from datetime import datetime
from pathlib import Path

import msgspec
from dotenv import load_dotenv
from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel

load_dotenv()
WATCH_DIRECTORY = Path("watchlist")
WATCH_EXTENSION = os.getenv("WATCH_EXTENSION", ".mp4;.mkv;.avi;.nfo;.srt").split(";")
EXCLUDE_FILE = os.getenv("EXCLUDE_FILE", "tvshow.nfo;season.nfo").split(";")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = f"""
You will be assessing TV shows or animes' with file extensions in {WATCH_EXTENSION} for it's episode information based on the list of filepaths provided to you.
Show name should not include season number or episode number.
Use internet search to verify the show name, from sources like TMDB, TVDB, AniDB, etc.

Respond in JSON format with the provided JSON schema
"""


class EpisodeInfo(BaseModel):
    file_path: str
    show_name: str
    season_number: int
    episode_number: int
    is_special_season: bool


client = genai.Client(api_key=GEMINI_API_KEY)
model = "gemini-2.0-flash"


def rename_series(filenames: list[str]):
    response = client.models.generate_content(
        model=model,
        contents=[SYSTEM_PROMPT, str(filenames)],
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[EpisodeInfo],
        ),
    )
    response_dict = []
    try:
        pass
        response_dict = msgspec.json.decode(response.text)
    except ValueError as e:
        print(f"Invalid JSON format from response: {response.text}")
    return response_dict


def is_renamed(episode_name: str):
    is_renamed = re.search(r"S\d+E\d+", episode_name)
    if is_renamed:
        return True
    return False


def rename_episode(
    episode_path: Path,
    show_name: str,
    season_number: int,
    episode_number: int,
    is_special_season: bool,
):
    file = Path(episode_path)
    if file.is_file():
        if is_special_season:
            new_filename = f"{show_name} S00E{episode_number:02d}{file.suffix}"
        else:
            new_filename = (
                f"{show_name} S{season_number:02d}E{episode_number:02d}{file.suffix}"
            )
        file.rename(Path(file.parent, new_filename))
        print(
            f"Renaming: {str(file.relative_to(WATCH_DIRECTORY))} -> {str(Path(file.parent.relative_to(WATCH_DIRECTORY), new_filename))}\n"
        )
    else:
        print(f"Unable to rename {str(file)}, file doesn't exist?\n")


def start_rename():
    all_folders = []
    print("-" * 50)
    print(f"Run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Watching directory: ")
    if WATCH_DIRECTORY.is_dir():
        detect_folders = [
            Path(folder) for folder in WATCH_DIRECTORY.iterdir() if folder.is_dir()
        ]
        all_folders.extend(detect_folders)

    for folder in all_folders:
        print(f"- {folder.name}")

    for index, series in enumerate(all_folders):
        episodes = [
            episode
            for episode in series.rglob("*")
            if episode.suffix in WATCH_EXTENSION
            and not is_renamed(episode.name)
            and episode.name not in EXCLUDE_FILE
        ]
        if episodes:
            ai_results = rename_series(episodes)
            for episode_info in ai_results:
                relative_path = Path(episode_info["file_path"]).relative_to(
                    Path("watchlist")
                )
                if match := next(
                    (
                        real_path
                        for real_path in episodes
                        if str(relative_path) in str(real_path)
                    ),
                    None,
                ):
                    rename_episode(
                        match,
                        episode_info["show_name"],
                        episode_info["season_number"],
                        episode_info["episode_number"],
                        episode_info["is_special_season"],
                    )
            if index == len(all_folders) - 1:  # Check if last iteration
                break
            else:
                time.sleep(5)


if __name__ == "__main__":
    start_rename()
    # print(
    #     Path(
    #         "/watchlist/bangumi/test/Season 4/[Sakurato] Sousou no Frieren [21][AVC-8bit 1080p AAC][CHT].nfo"
    #     ).relative_to(Path("/watchlist"))
    # )
    # test = [
    #     "/bangumi/[Sakurato] Sousou no Frieren Season 2 [22][AVC-8bit 1080p AAC][CHT].mp4",
    #     "/Season 3/[Nekomoe kissaten&LoliHouse] Kono Sekai wa Fukanzen Sugiru - 04 [WebRip 1080p HEVC-10bit AAC ASSx2].mkv",
    # ]
    # print(rename_series(test))
