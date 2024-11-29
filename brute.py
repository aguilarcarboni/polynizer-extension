import time
import math
import pandas as pd
import os
import itertools
import logging
from typing import List, Tuple, Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger()

# Function to calculate centroids of chord variants
def get_variant_centroids(chord: str, df: pd.DataFrame) -> Tuple[float, float, float]:
    if chord not in df.index:
        logger.warning(f"Chord {chord} not found in DataFrame!")
        return 10000.0, 10000.0, 10000.0  # Consistent handling of invalid chords

    placements = df.loc[chord].fillna(-1).tolist()
    variants = []

    for i in range(0, 20, 7):
        fret = placements[i]
        if fret == -1:  # Open or unplayed string
            fret = 0
        elif fret > 7:  # Invalid fret
            variants.append(10000.0)
            continue

        total_sum = 0
        divisor = 6
        for x in placements[i + 1:i + 7]:
            if x == -1:  # Unplayed string
                divisor -= 1
            else:
                total_sum += fret + x  # Sum of fret position and finger positions

        if divisor > 0:
            variants.append(total_sum / divisor)
        else:
            variants.append(10000.0)  # Consistent invalid variant handling

    logger.debug(f"Chord: {chord}, Variants: {variants}")
    return tuple(variants)

# Function to calculate displacement between centroids
def calculate_displacement(combination: Tuple[float, ...]) -> float:
    try:
        displacement = sum((combination[i] - combination[i - 1]) ** 2 for i in range(1, len(combination)))
        return displacement
    except (TypeError, ValueError):
        return float('inf')  # Handle unexpected invalid values in combinations

# Brute-force logic with precomputed centroids
def find_min_displacement_with_precomputed(song: List[str], centroids: Dict[str, Tuple[float, float, float]]) -> Tuple[float, List[float]]:
    variants = [centroids[chord] for chord in song]
    logger.info("All chord variants prepared from precomputed centroids.")

    valid_combinations = itertools.product(*variants)
    logger.info("Starting brute-force iteration...")

    min_displacement = float('inf')
    best_path = []
    combination_count = 0
    start_combination_logging = time.time()

    for combination in valid_combinations:
        combination_count += 1

        # Log progress for every 100,000 combinations
        if combination_count % 100000 == 0:
            elapsed = time.time() - start_combination_logging
            logger.info(f"Checked {combination_count} combinations so far... (Elapsed time: {elapsed:.2f}s)")

        # Skip combinations containing invalid centroids
        if any(variant == 10000.0 for variant in combination):
            continue

        displacement = calculate_displacement(combination)

        if displacement < min_displacement:
            min_displacement = displacement
            best_path = combination
            logger.info(f"New minimum displacement: {min_displacement}")

    logger.info(f"Total combinations checked: {combination_count}")
    return min_displacement, best_path

# Function to save results to a file
def save_results(file_path: str, song: List[str], min_displacement: float, best_path: List[float]) -> None:
    with open(file_path, 'w') as file:
        file.write(f"Minimum Displacement: {min_displacement}\n")
        file.write(f"Sqrt(total cost): {math.sqrt(min_displacement):.2f}\n")
        file.write("Optimal Path:\n")
        for chord, variant in zip(song, best_path):
            file.write(f"{chord} = play with centroid {variant}\n")
    logger.info(f"Results saved to {file_path}")

# Precompute centroids for all chords in the DataFrame
def precompute_centroids(df: pd.DataFrame) -> Dict[str, Tuple[float, float, float]]:
    centroids = {}
    for chord in df.index:
        centroids[chord] = get_variant_centroids(chord, df)
    logger.info("Centroids precomputed for all chords in the DataFrame.")
    return centroids

# Load the song
def load_song(file_path: str) -> List[str]:
    if not os.path.exists(file_path):
        logger.error("File not found!")
        return []
    
    with open(file_path, 'r') as file:
        chords = [line.strip().lower() for line in file]
    
    logger.info(f"File loaded successfully with {len(chords)} chords.")
    return chords


# ------------------------------- #
# Constants
file_path = 'songs/song2.txt'
results_file = 'lib/results.txt'

song = load_song(file_path)

# Load the chord data
try:
    df_temp = pd.read_excel('lib/GuitarDict.xlsx')
    df = df_temp.set_index(df_temp.columns[0])  # Use the first column (chord names) as the index
    df.index = df.index.str.strip().str.lower()  # Clean index values
    logger.info("DataFrame loaded successfully.")
except Exception as e:
    logger.error(f"Error loading GuitarDict.xlsx: {e}")
    exit(1)

# Filter song to valid chords
song = [chord for chord in song if chord in df.index]
if not song:
    logger.error("No valid chords found in the song!")
    exit(1)

logger.info(f"Filtered song list: {song}")

# Precompute centroids
centroids = precompute_centroids(df)

# Measure time and find the minimum displacement
start_time = time.time()
min_displacement, best_path = find_min_displacement_with_precomputed(song, centroids)
end_time = time.time()

# Display results
logger.info(f"Iteration complete in {(end_time - start_time) * 1000:.2f} ms.")
logger.info(f"Minimum displacement: {min_displacement}")
logger.info(f"Sqrt(total cost): {math.sqrt(min_displacement):.2f}")
logger.info("Optimal Path:")

for i, (chord, variant) in enumerate(zip(song, best_path)):
    if i == 0:
        chord_cost = 0
    else:
        chord_cost = sum((variant - best_path[j]) ** 2 for j in range(i))
    sqrt_cost = math.sqrt(chord_cost)
    logger.info(f"{chord} = play with centroid {variant}, sqrt(total cost): {sqrt_cost:.2f}")

# Save results to a file
save_results(results_file, song, min_displacement, best_path)