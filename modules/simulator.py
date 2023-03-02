from modules.server import Server
from modules.event_handler import EventHandler


class Simulator:
    def __init__(self, **argv) -> None:
        self.application_server = Server(
            core_count = argv['application_server_count'],
            average_service_time = argv['application_service_time']
        )

        self.db_server = Server(
            core_count = argv['db_server_count'],
            average_service_time = argv['db_service_time']
        )

        self.event_queue = []   # Priority queue for event handler
        
        self.event_handler = EventHandler(
            event_queue = self.event_queue,
            application_server = self.application_server,
            db_server = self.db_server
        )

    def run(self):
        raise NotImplementedError