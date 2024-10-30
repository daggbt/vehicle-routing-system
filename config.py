from datetime import datetime, timedelta

# Perth CBD coordinates (Elizabeth Quay)
DEPOT_LOCATION = (-31.9523, 115.8613)

# Vehicle configurations
VEHICLE_CAPACITY = 1000
NUM_VEHICLES = 3

# Customer locations (suburb: coordinates)
PERTH_SUBURBS = {
    'Fremantle': (-32.0569, 115.7439),
    'Scarborough': (-31.8943, 115.7505),
    'Midland': (-31.8915, 116.0010),
    'Armadale': (-32.1506, 116.0137),
    'Joondalup': (-31.7430, 115.7629),
    'Victoria Park': (-31.9714, 115.8971),
    'Cottesloe': (-31.9927, 115.7547),
    'Belmont': (-31.9433, 115.9169),
    'Canning Vale': (-32.0547, 115.9075),
    'Morley': (-31.8865, 115.9006)
}

# Time window configurations
TIME_WINDOW_CONFIGS = {
    'early': (0, 2),    # 0-2 hours from now
    'mid': (1, 3),      # 1-3 hours from now
    'late': (2, 5),     # 2-5 hours from now
    'flexible': (0, 4)  # 0-4 hours from now
}

# Route optimization parameters
OPTIMIZATION_PARAMS = {
    'traffic_factor': 1.2,  # Default traffic multiplier
    'service_time_minutes': 10,  # Time spent at each customer
    'average_speed_kmh': 30,  # Average vehicle speed in km/h
    'max_route_duration_hours': 8,  # Maximum route duration
    'distance_matrix_precision': 2  # Decimal places for distance calculations
}

# Visualization settings
VIZ_CONFIG = {
    'map_zoom_start': 11,
    'depot_icon_color': 'red',
    'customer_icon_color': 'blue',
    'route_colors': ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF'],
    'plot_figsize': (15, 10)
}

# File paths
OUTPUT_PATHS = {
    'route_visualization': 'output/routes.html',
    'statistics_plot': 'output/route_statistics.png',
    'report_json': 'output/route_report.json',
    'log_file': 'output/vrs.log'
}