import folium
import matplotlib.pyplot as plt
import colorsys
from typing import Dict, List, Tuple
import json
from datetime import datetime
import os
from models import Customer
from config import VIZ_CONFIG, OUTPUT_PATHS

def safe_get_route_stat(route_statistics: Dict, route_id: int, key: str, default=0):
    """Safely get route statistics with fallback values"""
    try:
        return route_statistics.get(route_id, {}).get(key, default)
    except:
        return default

def create_route_visualization(depot_location: Tuple[float, float],
                             optimized_routes: Dict[int, List[Customer]],
                             route_statistics: Dict):
    """Create an interactive map visualization of all routes"""
    try:
        # Create base map centered on depot
        m = folium.Map(location=depot_location, 
                      zoom_start=VIZ_CONFIG['map_zoom_start'])
        
        # Add depot marker
        folium.Marker(
            depot_location,
            popup='Depot',
            icon=folium.Icon(color=VIZ_CONFIG['depot_icon_color'], 
                           icon='info-sign')
        ).add_to(m)
        
        # Generate distinct colors for each route
        num_routes = len(optimized_routes)
        colors = VIZ_CONFIG['route_colors'] * (num_routes // len(VIZ_CONFIG['route_colors']) + 1)
        
        # Plot each route
        for route_idx, (vehicle_id, customers) in enumerate(optimized_routes.items()):
            route_color = colors[route_idx]
            route_coords = [depot_location]  # Start at depot
            
            # Create feature group for route
            route_group = folium.FeatureGroup(f"Vehicle {vehicle_id}")
            
            # Add customer markers
            for customer in customers:
                route_coords.append(customer.location)
                
                # Calculate customer statistics
                demand = customer.demand
                priority = customer.priority
                time_windows = '<br>'.join([
                    f"Window {i+1}: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
                    for i, (start, end) in enumerate(customer.time_windows)
                ])
                
                # Create popup content
                popup_content = f"""
                <div style='font-family: Arial'>
                    <b>Customer {customer.id}</b><br>
                    Demand: {demand}<br>
                    Priority: {priority}<br>
                    Time Windows:<br>{time_windows}
                </div>
                """
                
                folium.Marker(
                    customer.location,
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=VIZ_CONFIG['customer_icon_color'], 
                                   icon='info-sign')
                ).add_to(route_group)
            
            route_coords.append(depot_location)  # Return to depot
            
            # Calculate route statistics
            route_stats = route_statistics.get(vehicle_id, {})
            distance = safe_get_route_stat(route_statistics, vehicle_id, 'final_distance', 0)
            num_customers = len(customers)
            
            # Create route popup content
            route_popup = f"""
            <div style='font-family: Arial'>
                <b>Route {vehicle_id}</b><br>
                Distance: {distance/1000:.2f} km<br>
                Customers: {num_customers}<br>
                Total Demand: {sum(c.demand for c in customers)}
            </div>
            """
            
            # Draw route line
            route_line = folium.PolyLine(
                route_coords,
                weight=2,
                color=route_color,
                opacity=0.8,
                popup=folium.Popup(route_popup, max_width=300)
            )
            route_line.add_to(route_group)
            
            route_group.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(OUTPUT_PATHS['route_visualization']), 
                   exist_ok=True)
        
        # Save map
        m.save(OUTPUT_PATHS['route_visualization'])
        print(f"Route visualization saved to {OUTPUT_PATHS['route_visualization']}")
        
    except Exception as e:
        print(f"Error creating route visualization: {e}")
        # Create a minimal map with just the depot
        m = folium.Map(location=depot_location, 
                      zoom_start=VIZ_CONFIG['map_zoom_start'])
        folium.Marker(
            depot_location,
            popup='Depot (Error occurred during visualization)',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
        
        os.makedirs(os.path.dirname(OUTPUT_PATHS['route_visualization']), 
                   exist_ok=True)
        m.save(OUTPUT_PATHS['route_visualization'])

def calculate_route_totals(optimized_routes: Dict[int, List[Customer]], 
                         route_statistics: Dict) -> Dict:
    """Calculate total statistics with fallback values"""
    totals = {
        'total_distance': 0,
        'total_demand': 0,
        'total_customers': 0,
        'high_priority_customers': 0
    }
    
    for route_id in optimized_routes.keys():
        totals['total_distance'] += safe_get_route_stat(route_statistics, route_id, 
                                                      'final_distance', 0)
        totals['total_demand'] += safe_get_route_stat(route_statistics, route_id, 
                                                    'total_demand', 0)
        totals['total_customers'] += safe_get_route_stat(route_statistics, route_id, 
                                                       'num_customers', 0)
        totals['high_priority_customers'] += safe_get_route_stat(
            route_statistics, route_id, 'high_priority_customers', 0)
    
    return totals

def generate_report(optimized_routes: Dict[int, List[Customer]], 
                   route_statistics: Dict,
                   total_optimization_time: float):
    """Generate a comprehensive JSON report with error handling"""
    try:
        # Calculate totals with fallback values
        totals = calculate_route_totals(optimized_routes, route_statistics)
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_optimization_time': total_optimization_time,
            'total_routes': len(optimized_routes),
            'total_customers': totals['total_customers'],
            'total_distance': totals['total_distance'],
            'total_demand': totals['total_demand'],
            'high_priority_customers': totals['high_priority_customers'],
            'routes': []
        }
        
        for vehicle_id, customers in optimized_routes.items():
            route_info = {
                'vehicle_id': vehicle_id,
                'num_customers': len(customers),
                'total_distance': safe_get_route_stat(route_statistics, vehicle_id, 'final_distance'),
                'total_demand': safe_get_route_stat(route_statistics, vehicle_id, 'total_demand'),
                'improvement': safe_get_route_stat(route_statistics, vehicle_id, 'improvement_percentage'),
                'high_priority_customers': safe_get_route_stat(
                    route_statistics, vehicle_id, 'high_priority_customers'),
                'customers': []
            }
            
            current_time = datetime.now()
            
            for customer in customers:
                customer_info = {
                    'id': customer.id,
                    'location': customer.location,
                    'demand': customer.demand,
                    'priority': customer.priority,
                    'time_windows': [
                        (tw[0].strftime('%H:%M:%S'), tw[1].strftime('%H:%M:%S'))
                        for tw in customer.time_windows
                    ]
                }
                route_info['customers'].append(customer_info)
            
            report['routes'].append(route_info)
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(OUTPUT_PATHS['report_json']), exist_ok=True)
        
        # Save report
        with open(OUTPUT_PATHS['report_json'], 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
        
    except Exception as e:
        print(f"Error generating report: {e}")
        # Return a minimal report
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'error': str(e),
            'total_routes': len(optimized_routes),
            'total_customers': sum(len(customers) for customers in optimized_routes.values())
        }

def create_statistics_plots(route_statistics: Dict):
    """Create statistical visualizations with error handling"""
    if not route_statistics:
        print("No route statistics available for plotting")
        return
    
    try:
        fig = plt.figure(figsize=VIZ_CONFIG['plot_figsize'])
        
        # Get available metrics
        routes = list(route_statistics.keys())
        
        # Plot only if we have data
        if routes:
            # Distance Improvement Plot
            plt.subplot(2, 2, 1)
            initial_distances = [safe_get_route_stat(route_statistics, r, 'initial_distance') 
                               for r in routes]
            final_distances = [safe_get_route_stat(route_statistics, r, 'final_distance') 
                             for r in routes]
            
            x = range(len(routes))
            plt.bar(x, initial_distances, alpha=0.5, label='Initial Distance')
            plt.bar(x, final_distances, alpha=0.5, label='Final Distance')
            plt.xlabel('Route ID')
            plt.ylabel('Distance (meters)')
            plt.title('Route Distance Improvement')
            plt.legend()
            
            # Customer Distribution
            plt.subplot(2, 2, 2)
            customers_per_route = [safe_get_route_stat(route_statistics, r, 'num_customers') 
                                 for r in routes]
            if any(customers_per_route):  # Only create pie chart if we have customers
                plt.pie(customers_per_route, labels=[f'Route {i}' for i in routes],
                        autopct='%1.1f%%')
                plt.title('Customer Distribution Across Routes')
            
            # Priority Distribution
            plt.subplot(2, 2, 3)
            high_priority = [safe_get_route_stat(route_statistics, r, 'high_priority_customers') 
                           for r in routes]
            total_customers = [safe_get_route_stat(route_statistics, r, 'num_customers') 
                             for r in routes]
            normal_priority = [t - h for t, h in zip(total_customers, high_priority)]
            
            width = 0.35
            plt.bar(routes, normal_priority, width, label='Normal Priority')
            plt.bar(routes, high_priority, width, bottom=normal_priority, label='High Priority')
            plt.xlabel('Route ID')
            plt.ylabel('Number of Customers')
            plt.title('Customer Priority Distribution')
            plt.legend()
        
        plt.tight_layout()
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(OUTPUT_PATHS['statistics_plot']), exist_ok=True)
        
        # Save plot
        plt.savefig(OUTPUT_PATHS['statistics_plot'])
        plt.close()
        
    except Exception as e:
        print(f"Error creating statistics plots: {e}")

def generate_report(optimized_routes: Dict[int, List[Customer]], 
                   route_statistics: Dict,
                   total_optimization_time: float):
    """Generate a comprehensive JSON report"""
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_optimization_time': total_optimization_time,
        'total_routes': len(optimized_routes),
        'total_customers': sum(len(route) for route in optimized_routes.values()),
        'total_distance': sum(route_statistics[i]['final_distance'] 
                            for i in optimized_routes.keys()),
        'routes': []
    }
    
    for vehicle_id, customers in optimized_routes.items():
        stats = route_statistics[vehicle_id]
        route_info = {
            'vehicle_id': vehicle_id,
            'num_customers': len(customers),
            'total_distance': stats['final_distance'],
            'total_demand': stats['total_demand'],
            'improvement': stats['improvement_percentage'],
            'high_priority_customers': stats['high_priority_customers'],
            'customers': [
                {
                    'id': customer.id,
                    'location': customer.location,
                    'demand': customer.demand,
                    'priority': customer.priority,
                    'time_windows': [
                        (tw[0].strftime('%H:%M:%S'), tw[1].strftime('%H:%M:%S'))
                        for tw in customer.time_windows
                    ]
                }
                for customer in customers
            ]
        }
        report['routes'].append(route_info)
    
    os.makedirs(os.path.dirname(OUTPUT_PATHS['report_json']), exist_ok=True)
    with open(OUTPUT_PATHS['report_json'], 'w') as f:
        json.dump(report, f, indent=2)
    
    return report