import time
from src.utils.logger import logger
from src.utils.chords_loader import chords_loader
from src.utils.song_loader import song_loader

from src.algorithms.dynamic import dynamic_stage, trace_path, print_results
from src.algorithms.bruteforce import brute_force_displacement, display_results
from src.algorithms.greedy import greedy_stage, print_greedy_results
number_of_chords = 15

logger.announcement("Welcome to the Polynizer Extension! We have compiled a list of four songs that take full advantage of our newly implemented algorithms.", 'info')
while True:
    logger.announcement("\nAvailable songs:", 'info_ns')
    logger.announcement("1. Halsey", 'info_ns')
    logger.announcement("2. Metallica", 'info_ns')
    logger.announcement("3. Catch the Rainbow", 'info_ns')
    logger.announcement("4. Luis Miguel", 'info_ns')

    logger.announcement("Select a song (1-4): ", 'info_ns')
    choice = input()
    
    if choice == '1':
        song_name = "Halsey"
        break
    elif choice == '2':
        song_name = "Metallica"
        break
    elif choice == '3':
        song_name = "Catch the Rainbow"
        break
    elif choice == '4':
        song_name = "Luis Miguel"
        break
    else:
        logger.announcement("Invalid choice. Please select 1, 2, 3, or 4.", 'error')

while True:
    logger.announcement("Enter the number of chords to use (0-20, multiples of 5, 0 for all): ", 'info_ns')
    number_of_chords = input()
    if number_of_chords.isdigit():
        number_of_chords = int(number_of_chords)
        if number_of_chords in range(0, 21, 5):  # Check if it's a multiple of 5 within the range
            break
        else:
            logger.announcement("Invalid input. Please enter a number that is a multiple of 5 between 0 and 20.", 'error')
    else:
        logger.announcement("Invalid input. Please enter a positive integer.", 'error')

while True:
    logger.announcement("Do you want to run the greedy algorithm? (y/n): ", 'info_ns')
    choice = input()
    if choice == 'y':
        run_greedy = True
        break
    elif choice == 'n':
        run_greedy = False
        break

if number_of_chords == 0:
    logger.announcement(f"Running algorithms for song {song_name} using all chords...", 'info')
else:
    logger.announcement(f"Running algorithms for song {song_name} using {number_of_chords} chords...", 'info')
time.sleep(2)

# Load necessary data
logger.announcement("Loading song and chord data...", 'info')
chords_df = chords_loader()
song, song_df = song_loader(chords_df, number_of_chords, song_name)
logger.announcement("Song and chord data loaded successfully.", 'success')
time.sleep(2)
# Run and measure time it takes to run dynamic programming
logger.announcement("Running dynamic programming...", 'info')
start_time = time.time()
chosen_row, F, G = dynamic_stage(song, chords_df)
path = trace_path(song, F, G, chosen_row)
end_time = time.time()
logger.announcement(f"Dynamic programming completed in {(end_time - start_time) * 1000:.2f} ms.", 'success')

logger.announcement("Displaying results for dynamic programming...", 'info')
print_results(path, chords_df, song_df)
time.sleep(2)

# Run and measure time it takes to run brute force
logger.announcement(f"Running brute force algorithm.", 'info')
start_time = time.time()
minimum_displacement, best_path = brute_force_displacement(song, chords_df)
end_time = time.time()
logger.announcement(f"Brute force completed in {(end_time - start_time) * 1000:.2f} ms.", 'success')

# Display results
logger.announcement("Displaying results for brute force...", 'info')
display_results(minimum_displacement, best_path, song_df)
time.sleep(2)

start_time = time.time()
path = greedy_stage(song, chords_df)
end_time = time.time()

elapsed_time = end_time - start_time
logger.info(f"Greedy algorithm completed in {elapsed_time * 1000:.2f} ms.")
print_greedy_results(path, chords_df, song_df)