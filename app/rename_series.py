import os
import re
import time
from datetime import datetime
from pathlib import Path

import google.generativeai as genai
import msgspec
import typing_extensions as typing
from dotenv import load_dotenv

load_dotenv()
WATCH_DIRECTORY = [Path("watchlist")]
WATCH_EXTENSION = (".mkv", ".mp4", ".nfo", ".avi")
EXCLUDE_NAME = ("tvshow.nfo", "season.nfo")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

SYSTEM_PROMPT = """
You will be assessing TV shows or animes' season number and episodes based on filepaths provided to you.
Response as JSON format with the following JSON schema without markdowns or markups:

file_to_rename = {"file_path": str, "show_name": str, "season_number": int, "episode_number": int,  "is_special_season": bool}
Return: {"files": list[file_to_rename]}
"""

def rename_series(filenames: list[str]):
    response = model.generate_content([SYSTEM_PROMPT, str(filenames)])
    response_data = response.text.replace("```json", "").replace("```", "")
    response_dict = {}
    try:
        response_dict = msgspec.json.decode(response_data)
    except ValueError as e:
        print(f"Invalid JSON format from response: {response.text}")
    return response_dict


def is_renamed(episode_name: str):
    is_renamed = re.search(r"S\d+E\d+", episode_name)
    if is_renamed:
        return True
    return False

def rename_episode(episode_path: Path, show_name: str, season_number: int, episode_number: int, is_special_season: bool):
    file = Path(episode_path)
    if file.is_file():
        if is_special_season:
            new_filename = f"{show_name} S00E{episode_number:02d}{file.suffix}"
        else:
            new_filename = f"{show_name} S{season_number:02d}E{episode_number:02d}{file.suffix}"
        file.rename(Path(file.parent, new_filename))
        print(f"Renaming: {str(file)} -> {str(Path(file.parent, new_filename))}\n")
    else:
        print(f"Unable to rename {str(file)}, file doesn't exist?\n")

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
            ai_results = rename_series(episodes)
            for episode in ai_results["files"]:
                rename_episode(episode["file_path"], episode["show_name"], episode["season_number"], episode["episode_number"], episode["is_special_season"])
            if index == len(all_folders) - 1:  # Check if last iteration
                break
            else:
                time.sleep(5)


if __name__ == "__main__":
    start_rename(WATCH_DIRECTORY)
    # test = ["[Sakurato] Sousou no Frieren Season 2 [22][AVC-8bit 1080p AAC][CHT]", "/Season 3/[Nekomoe kissaten&LoliHouse] Kono Sekai wa Fukanzen Sugiru - 04 [WebRip 1080p HEVC-10bit AAC ASSx2].mkv"]
    # print(type(rename_series(test)))
