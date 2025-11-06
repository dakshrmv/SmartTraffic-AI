# data_generator.py
import json
import time
import random
import os

DATA_FILE = 'traffic_data.json'
STATUS_FILE = 'light_status.json'
UPDATE_INTERVAL_SEC = 2 # How often to update the counts

# --- Simulation Parameters ---
MAX_CARS_PER_LANE = 120     # <<< ADDED: A hard cap for realism
# How many cars "leave" on a green light per cycle
CARS_LEAVING_PER_CYCLE = 10 
# How many cars "arrive" at a red light per cycle (min, max)
CARS_ARRIVING_MIN = 2
CARS_ARRIVING_MAX = 6

def read_light_status():
    """Reads the current light status (e.g., 'NS', 'EW', 'RED') from the file."""
    if not os.path.exists(STATUS_FILE):
        return "RED" # Default to all red
    try:
        with open(STATUS_FILE, 'r') as f:
            data = json.load(f)
            return data.get('active_phase', 'RED')
    except (IOError, json.JSONDecodeError):
        return "RED"

def write_traffic_data(car_counts):
    """Writes the current car counts to the data file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(car_counts, f)
    except IOError as e:
        print(f"Error writing data file: {e}")

def main():
    # Initial state of the simulation
    car_counts = {
        "n": 30, # North
        "s": 25, # South
        "e": 40, # East
        "w": 35  # West
    }
    
    print("Starting smart data generator...")
    print("This script will now run in a loop. Press Ctrl+C to stop.")

    while True:
        try:
            # 1. Read what the traffic light is doing
            active_phase = read_light_status()
            
            # 2. Realistically update car counts based on the light
            
            # Add new arriving cars (with some randomness)
            cars_arriving = random.randint(CARS_ARRIVING_MIN, CARS_ARRIVING_MAX)
            
            if active_phase == "NS":
                # N/S is GREEN: cars leave
                # E/W is RED: cars arrive
                car_counts['n'] = max(0, car_counts['n'] - CARS_LEAVING_PER_CYCLE)
                car_counts['s'] = max(0, car_counts['s'] - CARS_LEAVING_PER_CYCLE)
                car_counts['e'] += cars_arriving
                car_counts['w'] += cars_arriving
            
            elif active_phase == "EW":
                # E/W is GREEN: cars leave
                # N/S is RED: cars arrive
                car_counts['e'] = max(0, car_counts['e'] - CARS_LEAVING_PER_CYCLE)
                car_counts['w'] = max(0, car_counts['w'] - CARS_LEAVING_PER_CYCLE)
                car_counts['n'] += cars_arriving
                car_counts['s'] += cars_arriving
            
            else: # "RED" (all-red)
                # All lights are RED: cars arrive everywhere
                car_counts['n'] += cars_arriving
                car_counts['s'] += cars_arriving
                car_counts['e'] += cars_arriving
                car_counts['w'] += cars_arriving
            
            # 3. [NEW] Enforce a hard cap for realism
            car_counts['n'] = min(car_counts['n'], MAX_CARS_PER_LANE) # <<< ADDED
            car_counts['s'] = min(car_counts['s'], MAX_CARS_PER_LANE) # <<< ADDED
            car_counts['e'] = min(car_counts['e'], MAX_CARS_PER_LANE) # <<< ADDED
            car_counts['w'] = min(car_counts['w'], MAX_CARS_PER_LANE) # <<< ADDED
            
            # 4. Write the new data for the app to read
            write_traffic_data(car_counts)
            
            print(f"Status: {active_phase} | Updated Counts: N={car_counts['n']}, S={car_counts['s']}, E={car_counts['e']}, W={car_counts['w']}")
            
            # 5. Wait for the next update
            time.sleep(UPDATE_INTERVAL_SEC)
            
        except KeyboardInterrupt:
            print("\nStopping generator.")
            # Clear status file on exit
            if os.path.exists(STATUS_FILE):
                os.remove(STATUS_FILE)
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(UPDATE_INTERVAL_SEC)

if __name__ == "__main__":
    main()