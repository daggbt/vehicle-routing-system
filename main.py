# main.py
import os
from datetime import datetime, timedelta

from models import Customer, Vehicle
from routing_system import VehicleRoutingSystem
from visualization import (create_route_visualization, create_statistics_plots, 
                         generate_report)
from utils import setup_logging, create_output_directories
from config import (DEPOT_LOCATION, VEHICLE_CAPACITY, NUM_VEHICLES, 
                   PERTH_SUBURBS, TIME_WINDOW_CONFIGS)

def create_test_customers():
    """Create test customers with realistic Perth locations"""
    customers = []
    for i, (suburb, location) in enumerate(PERTH_SUBURBS.items(), 1):
        # Alternate between different time window configurations
        time_window_config = list(TIME_WINDOW_CONFIGS.values())[i % len(TIME_WINDOW_CONFIGS)]
        start_offset, end_offset = time_window_config
        
        customers.append(
            Customer(
                id=i,
                location=location,
                demand=150 + (i * 50) % 200,  # Varying demands between 150-350
                time_windows=[(
                    datetime.now() + timedelta(hours=start_offset),
                    datetime.now() + timedelta(hours=end_offset)
                )],
                priority=2 if i % 3 == 0 else 1  # Every third customer is high priority
            )
        )
    return customers

def main():
    """Main execution function"""
    try:
        # Setup logging and create output directories
        logger = setup_logging()
        create_output_directories()
        
        # Initialize system
        logger.info("Initializing VRS...")
        vrs = VehicleRoutingSystem(depot_location=DEPOT_LOCATION, logger=logger)
        
        # Add vehicles
        logger.info("Adding vehicles...")
        for i in range(NUM_VEHICLES):
            vehicle = Vehicle(
                id=i,
                capacity=VEHICLE_CAPACITY,
                start_location=DEPOT_LOCATION
            )
            vrs.add_vehicle(vehicle)
        
        # Add customers
        logger.info("Adding customers...")
        test_customers = create_test_customers()
        for customer in test_customers:
            vrs.add_customer(customer)
        
        # Optimize routes
        logger.info("Optimizing routes...")
        optimized_routes = vrs.optimize_routes()
        
        # Generate visualizations and reports
        logger.info("Generating visualizations and reports...")
        
        # Fix matplotlib backend issue
        os.environ['QT_QPA_PLATFORM']='offscreen'
        import matplotlib
        matplotlib.use('Agg')
        
        create_route_visualization(
            DEPOT_LOCATION,
            optimized_routes,
            vrs.route_statistics
        )
        
        create_statistics_plots(vrs.route_statistics)
        
        report = generate_report(
            optimized_routes,
            vrs.route_statistics,
            vrs.total_optimization_time
        )
        
        # Print summary
        logger.info("\nOptimization Summary:")
        logger.info(f"Total routes: {len(optimized_routes)}")
        logger.info(f"Total optimization time: {vrs.total_optimization_time:.2f} seconds")
        
        improvements = [stats['improvement_percentage'] 
                       for stats in vrs.route_statistics.values()]
        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            logger.info(f"Average improvement: {avg_improvement:.2f}%")
        
        # Print detailed route information
        logger.info("\nDetailed Route Information:")
        for vehicle_id, customers in optimized_routes.items():
            logger.info(f"\nRoute {vehicle_id}:")
            logger.info(f"Number of customers: {len(customers)}")
            logger.info(f"Total distance: {vrs.route_statistics[vehicle_id]['final_distance']/1000:.2f} km")
            logger.info("Stops:")
            for customer in customers:
                logger.info(f"  - {customer.id}: Priority {customer.priority}, "
                          f"Demand: {customer.demand}")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()