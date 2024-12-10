from typing import List, Tuple
import math
import pandas as pd
from src.utils.logger import logger

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
def display_results(minimum_displacement: float, best_path: List[Tuple[str, int, float]], csv_data: pd.DataFrame = None):
    logger.announcement("Run statistics:", 'info')
    logger.info(f"Minimum displacement: {minimum_displacement}")
    logger.info(f"Sqrt(total cost): {math.sqrt(minimum_displacement):.2f}")
    logger.announcement("Optimal Path:", 'info')
    
    cumulative_cost = 0
    for i, (chord, variant, centroid) in enumerate(best_path):
        if i == 0:
            cumulative_cost = 0
        else:
            cumulative_cost += (best_path[i][2] - best_path[i - 1][2]) ** 2
        sqrt_cost = math.sqrt(cumulative_cost)
        
        # Verify against CSV data if provided
        csv_verification = ""
        if csv_data is not None and i < len(csv_data):
            try:
                expected_l2 = csv_data.iloc[i]['L2 distance']
            except:
                expected_l2 = csv_data.iloc[i]['Sqrt(total cost)']

            diff = abs(sqrt_cost - expected_l2)
            if diff < 0.1:  # Allow small floating-point differences
                csv_verification = f"✓ (CSV: {expected_l2:.2f})"
            else:
                csv_verification = f"❌ (CSV: {expected_l2:.2f}, diff: {diff:.2f})"
        
        logger.announcement(
            f"For {chord} play variant {variant}. "
            f"Centroid: {centroid:.2f}, Total cost: {sqrt_cost:.2f} {csv_verification}", 
            'info_ns'
        )
