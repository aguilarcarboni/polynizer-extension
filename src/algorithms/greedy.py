
import math
from src.utils.logger import logger

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

def print_greedy_results(path, df, csv_data=None):
    logger.announcement("Displaying results for greedy:", 'info')
    
    for idx, (chord, variant, cost) in enumerate(path):
        centroid = get_centroids(chord, df)[variant]
        sqrt_cost = math.sqrt(cost)
        
        # Add CSV validation
        csv_verification = ""
        if csv_data is not None and idx < len(csv_data):
            try:
                expected_l2 = csv_data.iloc[idx]['L2 distance']
            except:
                expected_l2 = csv_data.iloc[idx]['Sqrt(total cost)']
                
            diff = abs(sqrt_cost - expected_l2)
            if diff < 0.1:  # Allow small floating-point differences
                csv_verification = f"✓ (CSV: {expected_l2:.2f})"
            else:
                csv_verification = f"❌ (CSV: {expected_l2:.2f}, diff: {diff:.2f})"
        
        logger.announcement(f"For {chord} play variant {variant}. "
                   f"Centroid: {centroid:.2f}, Total cost: {sqrt_cost:.2f} {csv_verification}", 'info_ns')