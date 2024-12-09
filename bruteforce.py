from typing import List, Tuple

import time
import os
import math
import pandas as pd

from utils.logger import logger

# TODO: Variable names and centroid functions

"""
get_centroids()
# Both files:
- Use the same logic for handling invalid variants (using -1 as placeholder)
- Process chord data in steps of 7 (range(0, 20, 7))
- Use similar centroid calculation logic with addition/divisor
- Handle invalid variants with a very large number (10000 vs 10000000)
- Use the same approach for checking invalid variants with placements[8:13]/[8:14] and placements[15:20]
"""

# The get_centroids function calculates average positions for a chord’s 
# 3 possible variants. These centroids represent the average positions of the fretboard and 
# string placements required to play each variant of the chord.
def get_centroids(chord: str, df: pd.DataFrame) -> List[float]:

    invalid = [-1, -1, -1, -1, -1]  # Placeholder for invalid variant indicators on the data
    placements = df.loc[chord].values.tolist()  # Fetch chord data from DataFrame
    placements = [-1.0 if math.isnan(x) else x for x in placements]  # Handle NaN values
    centroids = []  # List to store computed centroids for each variant

    # Compute centroids for each variant
    for i in range(0, 20, 7):  # The range (0, 20, 7) divides the chord data into three groups of 7 columns:i = 0 corresponds to the first variant.i = 7 corresponds to the second variant.i = 14 corresponds to the third variant.
        if placements[i] == -1:  # Non-existent variant
            fret = 0
        else:
            fret = placements[i] - 1  # Adjust fret number for calculations

        total_sum = 0  # Sum of fret positions and finger placements
        divisor = 6  # assumns all six strings are played. If not -1
        if placements[i] > 7:  # Invalid fret (outside playable range)
            centroids.append(10000.0)  # Mark as invalid
        else:
            for x in range(i + 1, i + 7):  # Process string placements
                if placements[x] == -1: 
                    divisor -= 1
                else:
                    total_sum += fret + placements[x]
            centroids.append(total_sum / divisor if divisor != 0 else 0)  # Avoid division by zero

    # Mark second and third variants as invalid if missing data, project instrution
    if placements[8:13] == invalid:
        centroids[1] = 10000.0
    if placements[15:20] == invalid:
        centroids[2] = 10000.0

    return centroids 

# Brute force logic to find the minimum displacement path
def brute_force_displacement(song: List[str], df: pd.DataFrame) -> Tuple[float, List[Tuple[str, int, float]]]:
    
    # Precompute centroids for all chords in the song
    logger.info("Precomputing centroids for all chords.")
    centroids = {chord: get_centroids(chord, df) for chord in song}
    logger.info("Centroids precomputed for all chords.")

    minimum_displacement = float('inf')  # Initialize minimum displacement
    best_path = []  # Initialize optimal path

    # Recursive helper function to explore all possible paths
    def explore(idx: int, current_path: List[Tuple[str, int, float]], cumulative_cost: float):
        
        nonlocal minimum_displacement, best_path #(keep track of the minimum displacement and the corresponding path)

        if idx == len(song):  # Base case: all chords have been processed
            if cumulative_cost < minimum_displacement:  # Update minimum if a better path is found
                minimum_displacement = cumulative_cost
                best_path = current_path[:]
            return

        current_chord = song[idx]  # Current chord being processed
        for variant in range(3):  # Explore all three variants for the current chord
            current_centroid = centroids[current_chord][variant]  # Get centroid for variant
            if current_centroid == 10000.0:  # Skip invalid variants
                continue

            # Calculate transition cost from previous centroid
            if idx > 0: #retrieve the centroid of the previous chord and calculate the transition cost
                prev_centroid = current_path[-1][2]  # Last centroid in the path
                transition_cost = (current_centroid - prev_centroid) ** 2
            else:
                transition_cost = 0  # No cost for the first chord

            # Recurse to the next chord
            explore(
                idx + 1,
                current_path + [(current_chord, variant, current_centroid)],  # Append current choice to path
                cumulative_cost + transition_cost,  # Update cumulative cost
            )

    # Start recursive exploration from the first chord
    explore(0, [], 0.0)
    return minimum_displacement, best_path  # Return the minimum displacement and corresponding path

# Function to display results in a readable format
def display_results(song: List[str], minimum_displacement: float, best_path: List[Tuple[str, int, float]]):
    logger.announcement("Run statistics:", 'info')
    logger.announcement(f"Minimum displacement: {minimum_displacement}", 'info')
    logger.announcement(f"Sqrt(total cost): {math.sqrt(minimum_displacement):.2f}", 'success')
    logger.info("Optimal Path:")
    cumulative_cost = 0  # Initialize cumulative cost for printing
    for i, (chord, variant, centroid) in enumerate(best_path):
        if i == 0:
            cumulative_cost = 0
        else:
            cumulative_cost += (best_path[i][2] - best_path[i - 1][2]) ** 2  # Update cost
        sqrt_cost = math.sqrt(cumulative_cost)
        logger.info(f"{chord} = play variant {variant} with centroid {centroid:.2f}, sqrt(total cost): {sqrt_cost:.2f}")

# Main function to load data, process the song, and display results
def main():
    
    songs_path = "lib/songs/"

    # File paths for the song and chord dictionary
    #file_path = "song1.txt" # Luis Miguel with 20 chords
    song_file_name = "song2.txt"  # Luis Miguel all chords
    #file_path = "song3.txt" # Metallica all chords
    #file_path = "song3.20chords.txt"  # Metallica 20 chords

    chord_dict_path = "lib/guitar_dict.xlsx"

    logger.announcement(f"Loading chord data for song: {song_file_name.split('.')[0]}", 'info')

    # Check if required files exist
    if not os.path.exists(songs_path + song_file_name) or not os.path.exists(chord_dict_path):
        logger.error("Required files not found!")
        return

    # Load song data from file
    with open(songs_path + song_file_name, 'r') as file:
        song = [line.strip().lower() for line in file]

    # Load chord data from Excel file
    # TODO pd.to_dict(orient='records') [{}, {}]
    try:
        df_temp = pd.read_excel(chord_dict_path)
        df = df_temp.set_index(df_temp.columns[0])  # Set the first column as the index
        df.index = df.index.str.strip().str.lower()  # Clean up index values
        logger.announcement("Chord data loaded successfully.", 'success')
    except Exception as e:
        logger.error(f"Error loading chord dictionary: {e}")
        return

    # Filter song to include only valid chords
    song = [chord for chord in song if chord in df.index]
    if not song:
        logger.error("No valid chords found in the song!")
        return

    # Run brute force algorithm to find the optimal path
    logger.announcement(f"Running brute force algorithm.", 'info')
    start_time = time.time()
    minimum_displacement, best_path = brute_force_displacement(song, df)
    end_time = time.time()

    # Display results
    logger.announcement(f"Brute force completed in {(end_time - start_time) * 1000:.2f} ms.", 'success')
    display_results(song, minimum_displacement, best_path)

if __name__ == "__main__":
    main()