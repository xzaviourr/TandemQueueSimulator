import settings

import sys
import argparse

from modules.simulator import Simulator


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web Server Simulation')
    parser.add_argument('--app_servers', type=int, required=True, help='number of application servers')
    parser.add_argument('--db_servers', type=int, required=True, help='number of database servers')
    parser.add_argument('--app_server_service_time', type=float, required=True, help='service time of application servers')
    parser.add_argument('--db_server_service_time', type=float, required=True, help='service time of database servers')
    parser.add_argument('--app_to_db_server_probability', type=float, required=True, 
                        help='probability of request going to database server from application server')
    parser.add_argument('--simulation_time', type=float, required=True, help='number of application servers')
    parser.add_argument('--num_clients', type=int, required=True, help='number of application servers')
    parser.add_argument('--think_time', type=float, required=True, help='think time of client')
    parser.add_argument('--priority_probability', type=float, required=True, help='probability of request being a priority request')
    parser.add_argument('--app_server_queue_length', type=float, required=True, help='length of app server queue')
    parser.add_argument('--db_server_queue_length', type=float, required=True, help='length of db server queue')
    parser.add_argument('--retry_delay', type=float, required=True, help='delay time after request timeout')
    parser.add_argument('--request_timeout', type=float, required=True, help='request timeout time')
    parser.add_argument('--db_call_is_synchronous', type=int, required=True, help='boolean flag to run the simulation with synchronous db calls')
    args = parser.parse_args()
    sim = Simulator(
        application_server_count = args.app_servers,
        db_server_count = args.db_servers,
        application_service_time = args.app_server_service_time,
        db_service_time = args.db_server_service_time,
        app_to_db_prob = args.app_to_db_server_probability,
        simulation_time = args.simulation_time,
        clients = args.num_clients,
        think_time = args.think_time,
        priority_prob = args.priority_probability,
        app_server_queue_length = args.app_server_queue_length,
        db_server_queue_length = args.db_server_queue_length,
        retry_delay = args.retry_delay,
        request_timeout = args.request_timeout,
        db_call_is_synchronous = args.db_call_is_synchronous
    )

    # sim = Simulator(
    #     application_server_count = 20,
    #     db_server_count = 5,
    #     application_service_time = 0.1,
    #     db_service_time = 1,
    #     app_to_db_prob = 0.02,
    #     simulation_time = 200,
    #     clients = 1360,
    #     think_time = 5,
    #     priority_prob = 0.2,
    #     app_server_queue_length = 1000,
    #     db_server_queue_length = 1000,
    #     retry_delay = 0.1,
    #     request_timeout = 20,
    #     db_call_is_synchronous = 1
    # )
    sim.run()