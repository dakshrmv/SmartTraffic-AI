# app.py - Complete Flask Web Application for Traffic Control System
# Place this file in the root of traffic-control-system folder

from flask import Flask, render_template, jsonify, request
import json
import os
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)

# === Configuration ===
DATA_FILE = 'traffic_data.json'
STATUS_FILE = 'light_status.json'
HISTORY_FILE = 'traffic_history.json'
SETTINGS_FILE = 'settings.json'

# Default settings
DEFAULT_SETTINGS = {
    'yellow_time': 2,
    'all_red_time': 1,
    'default_green_time': 5,
    'priority_time': 15,
    'demand_buffer': 10,
    'emergency_mode': False,
    'adaptive_mode': True,
    'rush_hour_mode': True,
    'pedestrian_mode': False
}

# === Helper Functions ===

def load_json_file(filename, default=None):
    """Load JSON data from file"""
    if not os.path.exists(filename):
        return default if default is not None else {}
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        # Silently handle JSON errors (normal during concurrent file access)
        # Only print if it's not a JSON decode error
        if "Expecting value" not in str(e):
            print(f"Error loading {filename}: {e}")
        return default if default is not None else {}

def save_json_file(filename, data):
    """Save JSON data to file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False

def get_traffic_data():
    """Get current traffic data"""
    return load_json_file(DATA_FILE, {"n": 0, "s": 0, "e": 0, "w": 0})

def get_light_status():
    """Get current light status"""
    return load_json_file(STATUS_FILE, {"active_phase": "RED", "timestamp": time.time()})

def set_light_status(phase):
    """Set light status"""
    data = {"active_phase": phase, "timestamp": time.time()}
    save_json_file(STATUS_FILE, data)

def get_settings():
    """Get system settings"""
    return load_json_file(SETTINGS_FILE, DEFAULT_SETTINGS)

def save_settings(settings):
    """Save system settings"""
    return save_json_file(SETTINGS_FILE, settings)

# === Traffic Control Logic ===

def adaptive_timing_logic():
    """Calculate optimal green time based on traffic"""
    data = get_traffic_data()
    settings = get_settings()
    
    # Extract traffic counts
    north_south = data.get('n', 0) + data.get('s', 0)
    east_west = data.get('e', 0) + data.get('w', 0)
    
    # Calculate timing based on demand
    ns_time = max(settings['default_green_time'], 
                  min(30, north_south // 2))
    ew_time = max(settings['default_green_time'], 
                  min(30, east_west // 2))
    
    return {'ns': ns_time, 'ew': ew_time}

def run_traffic_controller():
    """Background thread for automatic traffic control"""
    while True:
        try:
            settings = get_settings()
            
            if not settings.get('adaptive_mode', True):
                time.sleep(2)
                continue
            
            status = get_light_status()
            current_phase = status.get('active_phase', 'RED')
            
            timing = adaptive_timing_logic()
            
            # Cycle through phases
            if current_phase == 'RED':
                set_light_status('NS')
                time.sleep(timing['ns'])
            elif current_phase == 'NS':
                set_light_status('YELLOW_NS')
                time.sleep(settings.get('yellow_time', 2))
                set_light_status('RED')
                time.sleep(settings.get('all_red_time', 1))
                set_light_status('EW')
                time.sleep(timing['ew'])
            elif current_phase == 'EW':
                set_light_status('YELLOW_EW')
                time.sleep(settings.get('yellow_time', 2))
                set_light_status('RED')
                time.sleep(settings.get('all_red_time', 1))
                set_light_status('NS')
            
        except Exception as e:
            print(f"Error in traffic controller: {e}")
            time.sleep(5)

# === Routes - HTML Pages ===

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/demo')
@app.route('/demo.html')
def demo():
    """Demo page with live traffic simulation"""
    return render_template('demo.html')

@app.route('/problem')
@app.route('/problem.html')
def problem():
    """Problem statement page"""
    return render_template('problem.html')

@app.route('/solution')
@app.route('/solution.html')
def solution():
    """Solution overview page"""
    return render_template('solution.html')

@app.route('/features')
@app.route('/features.html')
def features():
    """Features page"""
    return render_template('features.html')

@app.route('/tech')
@app.route('/tech.html')
def tech():
    """Technology stack page"""
    return render_template('tech.html')

@app.route('/team')
@app.route('/team.html')
def team():
    """Team page"""
    return render_template('team.html')

# === API Routes ===

@app.route('/api/traffic')
def api_traffic():
    """Get current traffic data"""
    return jsonify(get_traffic_data())

@app.route('/api/status')
def api_status():
    """Get current light status"""
    return jsonify(get_light_status())

@app.route('/api/set_phase', methods=['POST'])
def api_set_phase():
    """Manually set traffic light phase"""
    data = request.get_json()
    phase = data.get('phase', 'RED')
    
    # Valid phases
    valid_phases = ['RED', 'NS', 'EW', 'YELLOW_NS', 'YELLOW_EW']
    
    if phase not in valid_phases:
        return jsonify({"error": "Invalid phase"}), 400
    
    set_light_status(phase)
    return jsonify({"success": True, "phase": phase})

@app.route('/api/emergency', methods=['POST'])
def api_emergency():
    """Set emergency mode"""
    data = request.get_json()
    direction = data.get('direction', 'NS')
    
    # Emergency override
    if direction in ['N', 'S']:
        set_light_status('NS')
    elif direction in ['E', 'W']:
        set_light_status('EW')
    else:
        set_light_status('RED')
    
    return jsonify({"success": True, "emergency": direction})

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Get or update system settings"""
    if request.method == 'GET':
        return jsonify(get_settings())
    else:
        data = request.get_json()
        settings = get_settings()
        settings.update(data)
        save_settings(settings)
        return jsonify({"success": True, "settings": settings})

@app.route('/api/history')
def api_history():
    """Get traffic history data"""
    history = load_json_file(HISTORY_FILE, [])
    return jsonify(history)

# === Initialize ===

def initialize_files():
    """Initialize JSON files if they don't exist"""
    if not os.path.exists(DATA_FILE):
        save_json_file(DATA_FILE, {"n": 0, "s": 0, "e": 0, "w": 0})
    
    if not os.path.exists(STATUS_FILE):
        save_json_file(STATUS_FILE, {"active_phase": "RED", "timestamp": time.time()})
    
    if not os.path.exists(SETTINGS_FILE):
        save_json_file(SETTINGS_FILE, DEFAULT_SETTINGS)
    
    if not os.path.exists(HISTORY_FILE):
        save_json_file(HISTORY_FILE, [])

# === Main ===

if __name__ == '__main__':
    print("=" * 60)
    print("🚦 SmartTraffic AI - Intelligent Traffic Management System")
    print("=" * 60)
    print("\nInitializing system...")
    
    # Initialize files
    initialize_files()
    print("✓ Data files initialized")
    
    # Start background traffic controller
    controller_thread = threading.Thread(target=run_traffic_controller, daemon=True)
    controller_thread.start()
    print("✓ Traffic controller started")
    
    print("\n" + "=" * 60)
    print("🌐 Server starting at http://localhost:5000")
    print("=" * 60)
    print("\n📋 Available pages:")
    print("   • http://localhost:5000/          - Home")
    print("   • http://localhost:5000/demo      - Live Demo")
    print("   • http://localhost:5000/problem   - Problem Statement")
    print("   • http://localhost:5000/solution  - Our Solution")
    print("   • http://localhost:5000/features  - Features")
    print("   • http://localhost:5000/tech      - Tech Stack")
    print("   • http://localhost:5000/team      - Team")
    print("\n📡 API Endpoints:")
    print("   • GET  /api/traffic    - Current traffic data")
    print("   • GET  /api/status     - Light status")
    print("   • POST /api/set_phase  - Set phase manually")
    print("   • POST /api/emergency  - Emergency override")
    print("\n💡 Tip: Run 'python data_generator.py' for realistic traffic simulation")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)