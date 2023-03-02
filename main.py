import settings

import sys

from modules.simulator import Simulator


if __name__ == "__main__":
    sim = Simulator(
        application_server_count = 2,
        db_server_count = 2,
        application_service_time = 1,
        db_service_time = 1,
        app_to_db_prob = 0.2,
        simulation_time = 100,
        think_time = 0.5,
        priority_prob = 0.2,
        clients = 10
    )
    sim.run()

    #TODO
    # Timeout implementation