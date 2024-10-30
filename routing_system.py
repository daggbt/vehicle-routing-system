from typing import List, Dict, Tuple
from datetime import datetime, timedelta 
import heapq
from collections import defaultdict
import numpy as np

from models import Customer, Vehicle
from utils import (calculate_distance, initialize_osm_graph, 
                  is_time_window_feasible, calculate_time_between_points)
from config import OPTIMIZATION_PARAMS

class VehicleRoutingSystem:
    def __init__(self, depot_location: Tuple[float, float], logger):
        self.depot = depot_location
        self.customers: List[Customer] = []
        self.vehicles: List[Vehicle] = []
        self.distance_matrix: Dict[Tuple[int, int], float] = {}
        self.traffic_multipliers: Dict[Tuple[int, int], float] = {}
        self.route_statistics = defaultdict(dict)
        self.total_optimization_time = 0
        self.logger = logger
        
        # Initialize graph
        self.graph = initialize_osm_graph(depot_location, logger)

    def add_customer(self, customer: Customer):
        """Add a new customer"""
        self.customers.append(customer)
        self.logger.info(f"Added customer {customer.id}")

    def add_vehicle(self, vehicle: Vehicle):
        """Add a new vehicle"""
        self.vehicles.append(vehicle)
        self.logger.info(f"Added vehicle {vehicle.id}")

    def clarke_wright_savings(self) -> List[List[Customer]]:
        """Generate initial solution using Clarke-Wright savings algorithm"""
        self.logger.info("Generating initial solution using Clarke-Wright algorithm")
        n = len(self.customers)
        savings = []
        
        for i in range(n):
            for j in range(i + 1, n):
                cust_i = self.customers[i]
                cust_j = self.customers[j]
                
                saving = (
                    calculate_distance(self.graph, self.depot, cust_i.location, self.logger) +
                    calculate_distance(self.graph, self.depot, cust_j.location, self.logger) -
                    calculate_distance(self.graph, cust_i.location, cust_j.location, self.logger)
                )
                
                heapq.heappush(savings, (-saving, (i, j)))

        routes = [[customer] for customer in self.customers]
        merged = set()

        while savings:
            saving, (i, j) = heapq.heappop(savings)
            if i not in merged and j not in merged:
                route_i = next(r for r in routes if any(c.id == self.customers[i].id for c in r))
                route_j = next(r for r in routes if any(c.id == self.customers[j].id for c in r))
                
                if route_i != route_j:
                    total_demand = sum(c.demand for c in route_i + route_j)
                    if total_demand <= self.vehicles[0].capacity:
                        routes.remove(route_i)
                        routes.remove(route_j)
                        routes.append(route_i + route_j)
                        merged.add(i)
                        merged.add(j)

        return routes

    def two_opt_improvement(self, route: List[Customer]) -> List[Customer]:
        """Apply 2-opt local search improvement"""
        if len(route) < 3:
            return route
            
        improved = True
        best_distance = self.calculate_route_distance(route)
        
        while improved:
            improved = False
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    new_route = route[:i] + route[i:j][::-1] + route[j:]
                    new_distance = self.calculate_route_distance(new_route)
                    
                    if new_distance < best_distance:
                        route = new_route
                        best_distance = new_distance
                        improved = True
                        break
                if improved:
                    break
                    
        return route

    def calculate_route_distance(self, route: List[Customer]) -> float:
        """Calculate total route distance including traffic factors"""
        if not route:
            return 0
            
        total_distance = 0
        current_loc = self.depot
        
        for customer in route:
            segment = (current_loc, customer.location)
            distance = calculate_distance(self.graph, current_loc, customer.location, self.logger)
            
            # Apply traffic multiplier
            multiplier = self.traffic_multipliers.get(segment, 
                                                    OPTIMIZATION_PARAMS['traffic_factor'])
            total_distance += distance * multiplier
            
            current_loc = customer.location
            
        # Return to depot
        total_distance += calculate_distance(self.graph, current_loc, self.depot, self.logger)
        return total_distance

    def check_time_window_feasibility(self, route: List[Customer]) -> bool:
        """Verify if route satisfies all time window constraints"""
        current_time = datetime.now()
        current_loc = self.depot
        
        for customer in route:
            distance = calculate_distance(self.graph, current_loc, customer.location, self.logger)
            travel_time = calculate_time_between_points(distance)
            arrival_time = current_time + timedelta(minutes=travel_time)
            
            if not is_time_window_feasible(arrival_time, customer.time_windows):
                return False
                
            # Add service time
            current_time = arrival_time + timedelta(
                minutes=OPTIMIZATION_PARAMS['service_time_minutes']
            )
            current_loc = customer.location
            
        return True

    def optimize_routes(self) -> Dict[int, List[Customer]]:
        """Main route optimization function with proper statistics tracking"""
        start_time = datetime.now()
        self.logger.info("Starting route optimization")
        
        initial_routes = self.clarke_wright_savings()
        optimized_routes = {}
        self.route_statistics = defaultdict(dict)
        
        for i, route in enumerate(initial_routes):
            if not route:
                continue
                
            # Calculate initial statistics
            initial_distance = self.calculate_route_distance(route)
            initial_demand = sum(c.demand for c in route)
            
            # Sort by priority within route
            route.sort(key=lambda x: x.priority, reverse=True)
            
            # Apply improvements
            improved_route = self.two_opt_improvement(route)
            final_distance = self.calculate_route_distance(improved_route)
            
            # Ensure all required statistics are stored
            self.route_statistics[i] = {
                'initial_distance': initial_distance,
                'final_distance': final_distance,
                'improvement_percentage': ((initial_distance - final_distance) / initial_distance * 100 
                                        if initial_distance > 0 else 0),
                'num_customers': len(improved_route),
                'total_demand': initial_demand,
                'high_priority_customers': sum(1 for c in improved_route if c.priority > 1)
            }
            
            if self.check_time_window_feasibility(improved_route):
                optimized_routes[i] = improved_route
            else:
                # Split route if not feasible
                split_point = len(improved_route) // 2
                optimized_routes[i] = improved_route[:split_point]
                
                if len(improved_route) > split_point:
                    # Handle split route statistics
                    new_route = improved_route[split_point:]
                    new_route_id = len(optimized_routes)
                    optimized_routes[new_route_id] = new_route
                    
                    # Calculate statistics for split route
                    new_distance = self.calculate_route_distance(new_route)
                    new_demand = sum(c.demand for c in new_route)
                    
                    self.route_statistics[new_route_id] = {
                        'initial_distance': new_distance,
                        'final_distance': new_distance,
                        'improvement_percentage': 0,
                        'num_customers': len(new_route),
                        'total_demand': new_demand,
                        'high_priority_customers': sum(1 for c in new_route if c.priority > 1)
                    }
        
        self.total_optimization_time = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Route optimization completed in {self.total_optimization_time:.2f} seconds")
        
        return optimized_routes