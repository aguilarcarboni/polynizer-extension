import pandas as pd
import math
import logging
import time
import os

from utils.logger import logger

# TODO change very large number to INF
INF = float('inf')
MINUS_INF = float('-inf')

def get_centroids(chord, df):
    invalid = [-1, -1, -1, -1, -1]

    # Get finger positions and deal with NaN values
    placements = df.loc[chord].values.tolist()
    placements = [-1.0 if math.isnan(x) else x for x in placements]

    # List to store centroids
    centroids = []

    for i in range(0, 20, 7):
        # Check if chord is NaN and fix
        if placements[i] == -1:
            fret = 0
        else:
            # Fix fret to work with finger values later
            fret = placements[i] - 1 
        
        total_sum = 0
        divisor = 6
        # If the chord is invalid, set the centroid to a very large number
        if placements[i] > 7:  
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

    # Check for non-existent chord placements
    if placements[8:13] == invalid:
        centroids[1] = 10000.0
    if placements[15:20] == invalid:
        centroids[2] = 10000.0

    return centroids

def dynamic_stage(song, df):
    # Displacement matrix (F) and path matrix (G)
    F = [[float('inf')] * len(song) for _ in range(3)]
    G = [[-1] * len(song) for _ in range(3)]

    # Initialize base case
    for i in range(3):
        F[i][0] = 0  # Start with zero cost
        G[i][0] = i  # Start with each variant

    # Fill DP table
    for idx in range(1, len(song)):
        prev_centroids = get_centroids(song[idx - 1], df)
        curr_centroids = get_centroids(song[idx], df)

        for i in range(3):  # Current variants
            min_cost = float('inf')
            best_prev_variant = -1
            for j in range(3):  # Previous variants
                if prev_centroids[j] >= 10000.0 or curr_centroids[i] >= 10000.0:
                    continue
                cost = (prev_centroids[j] - curr_centroids[i]) ** 2
                total_cost = F[j][idx - 1] + cost
                if total_cost < min_cost:
                    min_cost = total_cost
                    best_prev_variant = j
            F[i][idx] = min_cost
            G[i][idx] = best_prev_variant

    # Find the optimal last variant
    last_costs = [F[i][len(song) - 1] for i in range(3)]
    chosen_row = last_costs.index(min(last_costs))

    return chosen_row, F, G

def trace_path(song, F, G, chosen_row):
    path = []
    idx = len(song) - 1
    while idx >= 0:
        path.append((song[idx], chosen_row, F[chosen_row][idx]))
        chosen_row = G[chosen_row][idx]
        idx -= 1
    path.reverse()
    return path

def print_results(path, df):
    logger.info("Optimal Path:")
    cumulative_cost = 0
    for idx, (chord, variant, cost) in enumerate(path):
        centroid = get_centroids(chord, df)[variant]
        cumulative_cost = cost
        sqrt_cost = math.sqrt(cumulative_cost)
        logger.info(f"{chord} = play variant {variant} with centroid {centroid:.2f}, sqrt(total cost): {sqrt_cost:.2f}")

def main():
    songs_path = "lib/songs/"
    # Load song file
    #song_file = "song1.txt" #Luis Miguel con todos chords 90%
    #song_file = "song2.txt" #Luis Miguel 20 los acordes
    #song_file = "song3.txt" #Metallica todos los acordes 100%
    song_file = "song3.20chords.txt" #Metallica todos los acordes 100%
    #song_file = "song4.txt" #Taylor swift todos los acordes 90%
    #song_file = "song5.txt" #Halsey todos los acordes 100%
    #song_file = "song6.txt" #Toto todos los acordes 95%
    #song_file = "song7.txt" #Catch the rainbow todos los acordes 100%
    chord_dict_file = "lib/guitar_dict.xlsx"

    if not os.path.exists(songs_path + song_file) or not os.path.exists(chord_dict_file):
        logger.error("Required files not found!")
        return

    with open(songs_path + song_file, 'r') as file:
        song = [line.strip().lower() for line in file]

    # Load chord data
    try:
        df_temp = pd.read_excel(chord_dict_file)
        df = df_temp.set_index(df_temp.columns[0])
        df.index = df.index.str.strip().str.lower()
        logger.info("Chord data loaded successfully.")
    except Exception as e:
        logger.error(f"Error loading chord dictionary: {e}")
        return

    # Filter song to valid chords
    song = [chord for chord in song if chord in df.index]
    if not song:
        logger.error("No valid chords found in the song!")
        return
    logger.info(f"Filtered song: {song}")

    # Measure time and run dynamic programming
    start_time = time.time()
    chosen_row, F, G = dynamic_stage(song, df)
    path = trace_path(song, F, G, chosen_row)
    end_time = time.time()

    elapsed_time = end_time - start_time
    logger.info(f"Dynamic programming completed in {elapsed_time * 1000:.2f} ms.")
    print_results(path, df)

if __name__ == "__main__":
    main()