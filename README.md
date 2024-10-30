# Vehicle Routing System (VRS)

A comprehensive vehicle routing system implementation that solves the Vehicle Routing Problem with Time Windows (VRPTW) using various optimization techniques. The system is specifically configured for Perth, Western Australia, but can be adapted for any location.

## Table of Contents
- [Vehicle Routing System (VRS)](#vehicle-routing-system-vrs)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Algorithm Details](#algorithm-details)
    - [Clarke-Wright Savings Algorithm](#clarke-wright-savings-algorithm)
    - [Local Search Improvements](#local-search-improvements)
    - [Distance Calculation](#distance-calculation)
  - [Installation](#installation)
    - [Using Conda (Recommended)](#using-conda-recommended)
    - [Alternative Installation (pip)](#alternative-installation-pip)
  - [Project Structure](#project-structure)
  - [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Custom Usage](#custom-usage)
  - [Configuration](#configuration)
    - [Main Configuration Options (config.py)](#main-configuration-options-configpy)
  - [Visualization](#visualization)
  - [Output](#output)
    - [Sample Route Report](#sample-route-report)
  - [Extending the System](#extending-the-system)
    - [Adding New Features](#adding-new-features)
    - [Customizing Visualizations](#customizing-visualizations)

## Overview

This Vehicle Routing System helps optimize delivery routes while considering multiple constraints such as:
- Time windows for deliveries
- Vehicle capacity constraints
- Priority customers
- Real-time traffic conditions
- Multiple vehicles
- Dynamic customer demands

The system uses OpenStreetMap data for real-world distance calculations and provides interactive visualizations of the optimized routes.

## Features

- **Route Optimization**
  - Clarke-Wright savings algorithm for initial solution
  - 2-opt local search improvement
  - Time window feasibility checking
  - Priority-based customer ordering
  - Dynamic route adjustment capabilities

- **Real-world Integration**
  - OpenStreetMap integration for actual road networks
  - Real distance calculations
  - Traffic factor considerations
  - Multiple time window support

- **Visualization**
  - Interactive web-based route maps
  - Statistical analysis plots
  - Detailed performance metrics
  - Customer and depot visualization

- **Reporting**
  - Comprehensive JSON reports
  - Route statistics
  - Performance metrics
  - Time window compliance reports

## Algorithm Details

### Clarke-Wright Savings Algorithm
The system uses the Clarke-Wright savings algorithm to generate an initial solution:
1. Initially, each customer is served by a dedicated vehicle
2. Calculate savings for merging routes: S(i,j) = d(0,i) + d(0,j) - d(i,j)
3. Sort savings in descending order
4. Merge routes if feasible considering:
   - Vehicle capacity constraints
   - Time window constraints
   - Priority customer requirements

### Local Search Improvements
The initial solution is improved using:
1. **2-opt**: Removes route crossings by:
   - Considering all pairs of edges
   - Reversing segments when beneficial
   - Checking feasibility after changes

2. **Time Window Management**:
- Routes are checked for time window feasibility
- Infeasible routes are split into feasible sub-routes
- Service times are considered at each stop

### Distance Calculation
- Uses OpenStreetMap for real road networks
- Calculates actual driving distances
- Falls back to Euclidean distance when necessary
- Considers traffic multipliers for realistic estimates

## Installation

### Using Conda (Recommended)

1. Create a new conda environment:
```bash
conda create -n vrout python=3.12
conda activate vrout
```

2. Install required packages:
```bash
conda install -c conda-forge osmnx networkx numpy pandas
conda install -c conda-forge folium matplotlib seaborn pulp
```

3. Clone the repository:
```bash
git clone https://github.com/daggbt/vehicle-routing-system.git
cd vehicle-routing-system
```

### Alternative Installation (pip)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Project Structure

```
vehicle_routing_system/
├── config.py           # Configuration settings
├── models.py          # Data classes (Customer, Vehicle)
├── utils.py           # Utility functions
├── visualization.py   # Visualization functions
├── routing_system.py  # Core VRS implementation
├── main.py           # Main execution script
└── output/           # Output directory
    ├── routes.html
    ├── route_statistics.png
    ├── route_report.json
    └── vrs.log
```

## Usage

### Basic Usage

1. Run the system with default settings:
```bash
python main.py
```

2. Check the output directory for results:
- `output/routes.html`: Interactive map
- `output/route_statistics.png`: Performance plots
- `output/route_report.json`: Detailed report

### Custom Usage

1. Modify the configuration in `config.py`:
```python
# Update depot location
DEPOT_LOCATION = (-31.9523, 115.8613)  # Perth CBD

# Adjust vehicle parameters
VEHICLE_CAPACITY = 1000
NUM_VEHICLES = 3

# Add custom locations
PERTH_SUBURBS = {
    'Fremantle': (-32.0569, 115.7439),
    'Scarborough': (-31.8943, 115.7505),
    # Add more locations...
}
```

2. Create custom customer scenarios:
```python
from models import Customer
from datetime import datetime, timedelta

# Create customers
customer = Customer(
    id=1,
    location=(-31.9523, 115.8613),
    demand=200,
    time_windows=[(datetime.now(), datetime.now() + timedelta(hours=2))],
    priority=2
)
```

## Configuration

### Main Configuration Options (config.py)

```python
# Location settings
DEPOT_LOCATION = (-31.9523, 115.8613)

# Vehicle settings
VEHICLE_CAPACITY = 1000
NUM_VEHICLES = 3

# Time window configurations
TIME_WINDOW_CONFIGS = {
    'early': (0, 2),    # 0-2 hours from now
    'mid': (1, 3),      # 1-3 hours from now
    'late': (2, 5)      # 2-5 hours from now
}

# Optimization parameters
OPTIMIZATION_PARAMS = {
    'traffic_factor': 1.2,
    'service_time_minutes': 10,
    'average_speed_kmh': 30
}
```

## Visualization

The system provides three types of visualizations:

1. **Interactive Route Map** (routes.html)
- Shows all routes with different colors
- Clickable markers for depot and customers
- Time window information in popups
- Layer controls for individual routes

2. **Statistical Plots** (route_statistics.png)
- Distance improvement comparison
- Customer distribution
- Priority distribution
- Route efficiency metrics

3. **JSON Report** (route_report.json)
- Comprehensive route details
- Performance metrics
- Time window compliance
- Customer information

## Output

### Sample Route Report
```json
{
  "timestamp": "2024-10-30 17:05:57",
  "total_optimization_time": 0.531,
  "total_routes": 3,
  "total_customers": 10,
  "total_distance": 125463.2,
  "routes": [
    {
      "vehicle_id": 0,
      "num_customers": 4,
      "total_distance": 42185.6,
      "customers": [...]
    }
  ]
}
```

## Extending the System

### Adding New Features

1. **Custom Constraints**
```python
def check_custom_constraint(route: List[Customer]) -> bool:
    # Implementation
    return True
```

2. **New Optimization Methods**
```python
def custom_improvement(route: List[Customer]) -> List[Customer]:
    # Implementation
    return improved_route
```

### Customizing Visualizations

1. **Custom Map Styles**
```python
VIZ_CONFIG = {
    'map_zoom_start': 11,
    'route_colors': ['#FF0000', '#00FF00', '#0000FF']
}
```

2. **Additional Statistics**
```python
def create_custom_plot(route_statistics: Dict):
    # Implementation
    plt.savefig('custom_plot.png')
```

