import os
import time
from src.utils.logger import logger
import pandas as pd

def song_loader(chords_df, number_of_chords, song_name):

    logger.info("Loading song file...")

    # Load song file
    current_dir = os.getcwd()
    songs_path = current_dir + "/src/lib/songs/"

    if number_of_chords == 0:
        song_file = f"{song_name}.txt"
    else:
        song_file = f"{song_name}_{number_of_chords}.txt"

    song_df = pd.read_csv(songs_path + f"/sources/csv/{song_name}.csv")

    if not os.path.exists(songs_path + song_file):
        logger.error("Required files not found!")
        raise FileNotFoundError("Required files not found!")
    
    try:
        with open(songs_path + song_file, 'r') as file:
            song = [line.strip().lower() for line in file]
        logger.success("Song file loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading song file: {e}")
        raise Exception(f"Error loading song file: {e}")

    logger.info("Filtering song to valid chords...")
    song = [chord for chord in song if chord in chords_df.index]
    if not song:
        logger.error("No valid chords found in the song!")
        raise Exception("No valid chords found in the song!")
    logger.success(f"Success: {song}")
    return song, song_df
