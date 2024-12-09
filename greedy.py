import pandas as pd
import math
import time
import os

from utils.logger import logger

# TODO: Variable names and centroid functions

def get_centroids(chord, df):
    invalid = [-1, -1, -1, -1, -1]

    # Get finger positions and deal with NaN values
    placements = df.loc[chord].values.tolist()
    placements = [-1.0 if math.isnan(x) else x for x in placements]

    # List to store centroids
    centroids = []

    for i in range(0, 20, 7):
        if placements[i] == -1:  # originally NaN
            fret = 0
        else:
            fret = placements[i] - 1  # fix fret to work with finger values later
        
        total_sum = 0
        divisor = 6
        if placements[i] > 7:  # invalid chord
            fret = 10000.0
            centroids.append(fret)
        else:
            for x in range(i + 1, i + 7):  # go through chord variant
                if placements[x] == -1:
                    divisor -= 1
                else:
                    total_sum += (fret + placements[x])
            if divisor != 0:
                centroids.append(total_sum / divisor)
            else:
                centroids.append(0)

    # Check for non-existent 2nd and 3rd variants
    if placements[8:13] == invalid:
        centroids[1] = 10000.0
    if placements[15:20] == invalid:
        centroids[2] = 10000.0

    return centroids

def greedy_stage(song, df):
    # Initialize the path and cumulative cost
    path = []
    cumulative_cost = 0

    # Start with the first chord
    prev_centroids = get_centroids(song[0], df)
    chosen_variant = 0  # Default to the first variant
    path.append((song[0], chosen_variant, 0))

    # Process each chord in the song
    for idx in range(1, len(song)):
        curr_centroids = get_centroids(song[idx], df)
        min_cost = float('inf')
        best_variant = -1

        # Find the best variant for the current chord
        for i in range(3):  # Current variants
            if curr_centroids[i] >= 10000.0:  # Invalid variant
                continue
            cost = (prev_centroids[chosen_variant] - curr_centroids[i]) ** 2
            if cost < min_cost:
                min_cost = cost
                best_variant = i

        # Update cumulative cost and chosen variant
        cumulative_cost += min_cost
        chosen_variant = best_variant
        path.append((song[idx], chosen_variant, cumulative_cost))

        # Update previous centroids
        prev_centroids = curr_centroids

    return path

def print_greedy_results(path, df):

    logger.info("Greedy Path:")
    for idx, (chord, variant, cost) in enumerate(path):
        centroid = get_centroids(chord, df)[variant]
        sqrt_cost = math.sqrt(cost)
        logger.info(f"{chord} = play variant {variant} with centroid {centroid:.2f}, sqrt(total cost): {sqrt_cost:.2f}")

def main():
    songs_path = "lib/songs/"
    # Load song and chord data
    #song_file = "song1.txt" #Luis Miguel con todos chords 90%
    #song_file = "song2.txt" #Luis Miguel 20 los acordes
    song_file = "song3.txt" #Metallica todos los acordes 100%
    #song_file = "song3.20chords.txt" #Metallica todos los acordes 
    #song_file = "song4.txt" #Taylor swift todos los acordes 90%
    #song_file = "song5.txt" #Halsey todos los acordes 90%
    #song_file = "song6.txt" #Toto todos los acordes 90%
    #song_file = "song7.txt" #Catch the rainbow todos los acordes 90%
    chord_dict_file = "lib/guitar_dict.xlsx"

    if not os.path.exists(songs_path + song_file) or not os.path.exists(chord_dict_file):
        logger.error("Required files not found!")
        return

    with open(songs_path + song_file, 'r') as file:
        song = [line.strip().lower() for line in file]

    try:
        df_temp = pd.read_excel(chord_dict_file)
        df = df_temp.set_index(df_temp.columns[0])
        df.index = df.index.str.strip().str.lower()
        logger.info("Chord data loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading chord dictionary: {e}")
        return

    song = [chord for chord in song if chord in df.index]
    if not song:
        logger.error("No valid chords found in the song!")
        return
    logger.info(f"Filtered song: {song}")

    start_time = time.time()
    path = greedy_stage(song, df)
    end_time = time.time()

    elapsed_time = end_time - start_time
    logger.info(f"Greedy algorithm completed in {elapsed_time * 1000:.2f} ms.")
    print_greedy_results(path, df)

if __name__ == "__main__":
    main()