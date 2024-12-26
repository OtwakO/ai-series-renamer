import os
import re
import time
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
import msgspec
from dotenv import load_dotenv

load_dotenv()
WATCH_DIRECTORY = [Path("watchlist")]
WATCH_EXTENSION = (".mkv", ".mp4", ".nfo", ".avi")
EXCLUDE_NAME = ("tvshow.nfo", "season.nfo")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

SYSTEM_PROMPT = """
You will be renaming TV shows, animes from it's filename(s) for me.

Provide a new filename for each filename I provide to you, filenames will be provided to you in python list format, following the format of {{Show name}} S{{Season number}}E{{Episode number}}. Season number and episode number should be padded to two digits if only single digit.
Your response should be in JSON format with no markups like the following and nothing else should be included:


Use this JSON schema: {"{{Original filename}}": "{{New filename}}"}
Input: ["[Sakurato] Yuru Camp Season 2 [13][AVC-8bit 1080p AAC][CHT]"]
Output: {"[Sakurato] Yuru Camp Season 2 [13][AVC-8bit 1080p AAC][CHT]": "Yuru Camp S02E13"}

DO NOT INCLUDE ANY FORM OF MARKUP IN YOUR RESPONSE, SUCH AS ```json```, THIS IS IMPORTANT.
"""


def rename_series(filenames: list[str]):
    response = model.generate_content([SYSTEM_PROMPT, str(filenames)])
    response_data = response.text.replace("```json", "").replace("```", "")
    response_dict = {}
    try:
        response_dict = msgspec.json.decode(response_data)
    except ValueError as e:
        print(f"Invalid JSON format, please provide a valid JSON response. {e}")
    return response_dict


def is_renamed(episode_name: str):
    is_renamed = re.search(r"S\d+E\d+", episode_name)
    if is_renamed:
        return True
    return False


def start_rename(watch_directory: list[Path]):
    all_folders = []
    print("-" * 50)
    print(f"Run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Watching directory: ")
    for path in watch_directory:
        if path.is_dir():
            detect_folders = [
                Path(folder) for folder in path.iterdir() if folder.is_dir()
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
            and episode.name not in EXCLUDE_NAME
        ]
        if episodes:
            episode_names = [episode.stem for episode in episodes]
            ai_results = rename_series(episode_names)
            for episode in episodes:
                parent_directory = episode.parent
                if ai_results.get(episode.stem):
                    new_filename = f"{ai_results[episode.stem]}{episode.suffix}"
                    episode.rename(
                        Path(
                            parent_directory,
                            new_filename,
                        )
                    )
                    print(
                        f"Renaming: {str(episode)} -> {str(Path(parent_directory, new_filename))}\n"
                    )
                else:
                    print(f"Unable to rename {str(episode)}\n")
            if index == len(all_folders) - 1:  # Check if last iteration
                break
            else:
                time.sleep(5)


if __name__ == "__main__":
    # start_rename(WATCH_DIRECTORY)
    test = ["[Sakurato] Sousou no Frieren [26][AVC-8bit 1080p AAC][CHT]"]
    print(rename_series(test))
