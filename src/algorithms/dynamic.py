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

def print_results(path, df, csv_data=None):
    logger.announcement("Optimal Path:", 'info')
    cumulative_cost = 0
    
    for idx, (chord, variant, cost) in enumerate(path):
        centroid = get_centroids(chord, df)[variant]
        cumulative_cost = cost
        sqrt_cost = math.sqrt(cumulative_cost)
        
        # Verify against CSV data if provided
        csv_verification = ""
        if csv_data is not None and idx < len(csv_data):
            try:
                expected_l2 = csv_data.iloc[idx]['L2 distance']
            except:
                expected_l2 = csv_data.iloc[idx]['Sqrt(total cost)']
            diff = abs(sqrt_cost - expected_l2)
            if diff < 0.1:
                csv_verification = f"✓ (CSV: {expected_l2:.2f})"
            else:
                csv_verification = f"❌ (CSV: {expected_l2:.2f}, diff: {diff:.2f})"
        
        logger.announcement(
            f"For {chord} play variant {variant}. "
            f"Centroid: {centroid:.2f}, Total cost: {sqrt_cost:.2f} {csv_verification}", 
            'info_ns'
        )