import settings

import heapq

from modules.server import Server
from modules.event_handler import EventHandler
from modules.event import Event
from modules.request import Request
from utils.probability_gen import get_probablity
from utils.logger import get_logger


class Simulator:
    def __init__(self, **argv) -> None:
        self.logger = get_logger("EVENT_HANDLER")
        
        self.simulation_time = argv['simulation_time']
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
            db_server = self.db_server,
            app_to_db_prob = argv["app_to_db_prob"],
            think_time = argv['think_time'],
            priority_prob = argv['priority_prob'],
            logger = self.logger
        )

        self.num_clients = argv['clients']
    
        self.initialize_simulation(priority_prob = argv['priority_prob'])

    def initialize_simulation(self, priority_prob):
        self.logger.info("INITIALIZING SIMULATION ...")
        
        for i in range(self.num_clients):
            heapq.heappush(
                self.event_queue,
                Event(
                    type = settings.EVENT_REQUEST_ARRIVAL,
                    request = Request(
                        request_priority = int(get_probablity(priority_prob)),
                        request_timeout = settings.REQUEST_TIMEOUT,
                        need_server = settings.APPLICATION_SERVER,
                        arrival_time = 0
                    ),
                    time = 0
                )
            )

    def run(self):
        self.logger.info("SIMULATION STARTED ...")

        current_time = 0
        while current_time < self.simulation_time:
            event = heapq.heappop(self.event_queue)
            current_time = event.time
            self.event_handler.handle_event(
                event = event,
                current_time = current_time
            )

        print(f"""
system throughput : {self.event_handler.request_completed_from_system/self.simulation_time} reqs/sec
app server throughput : {self.event_handler.request_completed_from_app_counter/self.simulation_time} reqs/sec
db server throughput : {self.event_handler.request_completed_from_db_counter/self.simulation_time} reqs/sec

system average response time : {self.event_handler.average_response_time_of_system} sec
app server average response time : {self.event_handler.average_response_time_of_app_server} sec
db server average response time : {self.event_handler.average_response_time_of_db_server} sec

number in system : {self.event_handler.number_in_system}
number in app server : {self.event_handler.number_in_app_server}
number in db app server : {self.event_handler.number_in_db_server}

requests dropped : {self.event_handler.request_dropped}
total requests served : {self.event_handler.request_completed_from_system}
fraction of requests dropped : {round((self.event_handler.request_dropped)/(self.event_handler.request_completed_from_system + self.event_handler.request_dropped),3)}
        """)