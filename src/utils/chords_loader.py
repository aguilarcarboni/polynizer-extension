import os
import pandas as pd
from src.utils.logger import logger

def chords_loader():

    logger.info("Loading chord dictionary...")

    # Load chord dictionary
    current_dir = os.getcwd()
    chord_dict_path = current_dir + "/src/lib/chords/"
    chord_dict_filename = "guitar_dict.xlsx"
    if not os.path.exists(chord_dict_path + chord_dict_filename):
        logger.error("Required files not found!")
        raise FileNotFoundError("Required files not found!")

    # Read file
    try:
        df_temp = pd.read_excel(chord_dict_path + chord_dict_filename)
        df = df_temp.set_index(df_temp.columns[0])
        df.index = df.index.str.strip().str.lower()
        logger.success("Chord data loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading chord dictionary: {e}")
        raise Exception(f"Error loading chord dictionary: {e}")

    return df