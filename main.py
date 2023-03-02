import settings

import sys

from modules import simulator


if __name__ == "__main__"():
    sim = simulator(
        application_server_count = 2,
        db_server_count = 2
    )

    sim.run()