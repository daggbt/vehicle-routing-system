import logging
import os
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import numpy as np
import osmnx as ox
import networkx as nx
from config import OPTIMIZATION_PARAMS, OUTPUT_PATHS

import warnings

warnings.filterwarnings('ignore', category=FutureWarning) 


def setup_logging():
    """Configure logging for the application"""
    os.makedirs(os.path.dirname(OUTPUT_PATHS['log_file']), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(OUTPUT_PATHS['log_file']),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('VRS')

def initialize_osm_graph(depot_location: Tuple[float, float], logger):
    """Initialize OpenStreetMap graph for the service area"""
    try:
        logger.info("Downloading map data...")
        lat, lon = depot_location
        delta = 0.1  # Roughly 11km at the equator
        bbox = (
            lon - delta,  # left
            lat - delta,  # bottom
            lon + delta,  # right
            lat + delta   # top
        )
        
        graph = ox.graph_from_bbox(
            north=bbox[3],
            south=bbox[1],
            east=bbox[2],
            west=bbox[0],
            network_type='drive',
            simplify=True,
            clean_periphery=True
        )
        
        try:
            graph = ox.speed.add_edge_speeds(graph)
            graph = ox.speed.add_edge_travel_times(graph)
        except Exception as e:
            logger.warning(f"Could not add speeds/travel times: {e}")
            for u, v, k, data in graph.edges(keys=True, data=True):
                data['speed_kph'] = data.get('speed_kph', 
                    OPTIMIZATION_PARAMS['average_speed_kmh'])
                length = data.get('length', 1000)
                data['travel_time'] = length / (data['speed_kph'] * 1000 / 3600)
        
        logger.info("Map data downloaded and processed successfully")
        return graph
        
    except Exception as e:
        logger.error(f"Error initializing map: {e}")
        logger.info("Creating fallback graph for testing")
        graph = nx.Graph()
        graph.add_node(1, y=depot_location[0], x=depot_location[1])
        return graph

def calculate_distance(graph: nx.Graph, point1: Tuple[float, float], 
                      point2: Tuple[float, float], logger) -> float:
    """Calculate shortest path distance between two points"""
    try:
        if graph is None or isinstance(graph, nx.Graph):
            return euclidean_distance(point1, point2)
        
        orig_node = ox.distance.nearest_nodes(
            graph, point1[1], point1[0], return_dist=True)[0]
        dest_node = ox.distance.nearest_nodes(
            graph, point2[1], point2[0], return_dist=True)[0]
        
        try:
            path_length = nx.shortest_path_length(
                graph, 
                orig_node, 
                dest_node, 
                weight='travel_time'
            )
            return path_length * 1000  # Convert to meters
        except nx.NetworkXNoPath:
            logger.warning(f"No path found between nodes {orig_node} and {dest_node}")
            return euclidean_distance(point1, point2)
            
    except Exception as e:
        logger.error(f"Error in distance calculation: {e}")
        return euclidean_distance(point1, point2)

def euclidean_distance(point1: Tuple[float, float], 
                      point2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points"""
    return np.sqrt(
        (point1[0] - point2[0])**2 + 
        (point1[1] - point2[1])**2
    ) * 111000  # Convert to meters (rough approximation)

def calculate_time_between_points(distance: float) -> float:
    """Calculate travel time in minutes between two points"""
    speed_mps = OPTIMIZATION_PARAMS['average_speed_kmh'] * 1000 / 3600
    return (distance / speed_mps) / 60  # Convert to minutes

def is_time_window_feasible(arrival_time: datetime, 
                          time_windows: List[Tuple[datetime, datetime]]) -> bool:
    """Check if arrival time falls within any time window"""
    return any(start <= arrival_time <= end for start, end in time_windows)

def create_output_directories():
    """Create necessary output directories"""
    for path in OUTPUT_PATHS.values():
        os.makedirs(os.path.dirname(path), exist_ok=True)