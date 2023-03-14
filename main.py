import settings

import sys
import argparse

from modules.simulator import Simulator


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Web Server Simulation')
    # parser.add_argument('--app_servers', type=int, required=True, help='number of application servers')
    # parser.add_argument('--db_servers', type=int, required=True, help='number of database servers')
    # parser.add_argument('--app_server_service_time', type=float, required=True, help='service time of application servers')
    # parser.add_argument('--db_server_service_time', type=float, required=True, help='service time of database servers')
    # parser.add_argument('--app_to_db_server_probability', type=float, required=True, 
    #                     help='probability of request going to database server from application server')
    # parser.add_argument('--simulation_time', type=float, required=True, help='number of application servers')
    # parser.add_argument('--num_clients', type=int, required=True, help='number of application servers')
    # parser.add_argument('--think_time', type=float, required=True, help='think time of client')
    # parser.add_argument('--priority_probability', type=float, required=True, help='probability of request being a priority request')

    # args = parser.parse_args()

    sim = Simulator(
        application_server_count = 50,
        db_server_count = 50,
        application_service_time = 0.2,
        db_service_time = 1,
        app_to_db_prob = 0.3,
        simulation_time = 30,
        clients = 10000,
        think_time = 5,
        retry_delay = 0.5,
        priority_prob = 0.2,
        app_server_queue_length = 100,
        db_server_queue_length = 100

        # application_server_count = args.app_servers,
        # db_server_count = args.db_servers,
        # application_service_time = args.app_server_service_time,
        # db_service_time = args.db_server_service_time,
        # app_to_db_prob = args.app_to_db_server_probability,
        # simulation_time = args.simulation_time,
        # clients = args.num_clients,
        # think_time = args.think_time,
        # priority_prob = args.priority_probability
    )
    sim.run()