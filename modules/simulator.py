import settings

import heapq
import os 
import pandas as pd
from modules.server import Server
from modules.event_handler import EventHandler
from modules.event import Event
from modules.request import Request
from utils.probability_gen import get_probablity
from utils.logger import get_logger


class Simulator:
    def __init__(self, **argv) -> None:
        """Simulator instance
        """
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
            logger = self.logger,
            app_server_queue_length = argv["app_server_queue_length"],
            db_server_queue_length = argv["db_server_queue_length"],
            retry_delay = argv['retry_delay'],
            request_timeout = argv['request_timeout'],
            db_call_is_synchronous = argv['db_call_is_synchronous']
        )

        self.num_clients = argv['clients']
        self.request_timeout = argv['request_timeout']
    
        self.initialize_simulation(priority_prob = argv['priority_prob'])

    def initialize_simulation(self, priority_prob):
        """Initialize the simulator with start events

        Args:
            priority_prob (float): Probability that request is of high priority
        """
        self.logger.info("INITIALIZING SIMULATION ...")
        
        for i in range(self.num_clients):
            heapq.heappush(
                self.event_queue,
                Event(
                    type = settings.EVENT_REQUEST_ARRIVAL,
                    request = Request(
                        request_priority = int(get_probablity(priority_prob)),
                        request_timeout = self.request_timeout,
                        need_server = settings.APPLICATION_SERVER,
                        arrival_time = 0
                    ),
                    time = 0
                )
            )

    def run(self):
        """Run the simulation
        """
        self.logger.info("SIMULATION STARTED ...")

        current_time = 0
        while current_time < self.simulation_time:
            event = heapq.heappop(self.event_queue)
            current_time = event.time
            self.event_handler.handle_event(
                event = event,
                current_time = current_time
            )

        results = pd.DataFrame({
            "num_clients" : [self.num_clients],
            "app_servers" : [self.event_handler.application_server.core_count],
            "db_servers" : [self.event_handler.db_server.core_count],
            "app_server_service_time" : [self.event_handler.application_server.average_service_time],
            "db_server_service_time" : [self.event_handler.db_server.average_service_time],
            "app_to_db_server_probability" : [self.event_handler.app_to_db_prob],
            "priority_probability" : [self.event_handler.priority_prob],
            "app_server_queue_length" : [self.event_handler.app_server_queue_length],
            "db_server_queue_length" : [self.event_handler.db_server_queue_length],
            "db_call_is_synchronous": [self.event_handler.db_call_is_synchronous],

            # "system_throughput" : [self.event_handler.request_completed_from_system/self.simulation_time],
            # "app_server_throughput" : [self.event_handler.request_completed_from_app_counter/self.simulation_time],
            # "db_server_throughput" : [self.event_handler.request_completed_from_db_counter/self.simulation_time],

            "system_throughput" : [(self.event_handler.request_completed_from_system_for_goodput + self.event_handler.request_completed_from_system_for_badput)/self.simulation_time],
            "app_server_throughput" : [(self.event_handler.request_completed_from_app_counter_for_goodput + self.event_handler.request_completed_from_app_counter_for_badput)/self.simulation_time],
            "db_server_throughput" : [(self.event_handler.request_completed_from_db_counter_for_goodput + self.event_handler.request_completed_from_db_counter_for_badput)/self.simulation_time],

            "system_goodput" : [self.event_handler.request_completed_from_system_for_goodput/self.simulation_time],
            "app_server_goodput" : [self.event_handler.request_completed_from_app_counter_for_goodput/self.simulation_time],
            "db_server_goodput" : [self.event_handler.request_completed_from_db_counter_for_goodput/self.simulation_time],

            "system_badput" : [self.event_handler.request_completed_from_system_for_badput/self.simulation_time],
            "app_server_badput" : [self.event_handler.request_completed_from_app_counter_for_badput/self.simulation_time],
            "db_server_badput" : [self.event_handler.request_completed_from_db_counter_for_badput/self.simulation_time],

            "system_average_response_time" : [self.event_handler.average_response_time_of_system],
            "app_server_average_response_time" : [self.event_handler.average_response_time_of_app_server],
            "db_server_average_response_time" : [self.event_handler.average_response_time_of_db_server],

            "number_in_system" : [self.event_handler.number_in_system],
            "number_in_app_server" : [self.event_handler.number_in_app_server],
            "number_in_db_app_server" : [self.event_handler.number_in_db_server],

            "priority_requests_dropped" : [self.event_handler.priority_request_dropped],
            "regular_requests_dropped" : [self.event_handler.regular_request_dropped],
            "total_requests_served" : [(self.event_handler.request_completed_from_system_for_goodput + self.event_handler.request_completed_from_system_for_badput)],
            "fraction_of_requests_dropped" : [round((self.event_handler.priority_request_dropped + self.event_handler.regular_request_dropped)/(self.event_handler.request_completed_from_system_for_goodput + self.event_handler.request_completed_from_system_for_badput + self.event_handler.priority_request_dropped + self.event_handler.regular_request_dropped),3)],

            "app_server_utilization" : [self.event_handler.application_server.busy_cores/self.event_handler.application_server.core_count],
            "db_server_utlization": [self.event_handler.db_server.busy_cores/self.event_handler.db_server.core_count]
        })

        # if file does not exist write header 
        if not os.path.isfile('RT_{}_simulation.csv'.format(self.request_timeout)):
            results.to_csv('RT_{}_simulation.csv'.format(self.request_timeout), header='column_names', index=False)
        else: # else it exists so append without writing the header
            results.to_csv('RT_{}_simulation.csv'.format(self.request_timeout), mode='a', header=False, index=False)

        print(f"""
-- SYSTEM CONFIGURATION --
num clients : {self.num_clients}
app servers : {self.event_handler.application_server.core_count}
db servers : {self.event_handler.db_server.core_count}
app server service time : {self.event_handler.application_server.average_service_time} seconds
db server service time : {self.event_handler.db_server.average_service_time} seconds
app to db server probability : {self.event_handler.app_to_db_prob}
priority probability : {self.event_handler.priority_prob}
app server queue length : {self.event_handler.app_server_queue_length}
db server queue length : {self.event_handler.db_server_queue_length}
synchronous db calls: {self.event_handler.db_call_is_synchronous}

-- RESULTS --
system throughput : {(self.event_handler.request_completed_from_system_for_goodput + self.event_handler.request_completed_from_system_for_badput)/self.simulation_time} reqs/sec
app server throughput : {(self.event_handler.request_completed_from_app_counter_for_goodput + self.event_handler.request_completed_from_app_counter_for_badput)/self.simulation_time} reqs/sec
db server throughput : {(self.event_handler.request_completed_from_db_counter_for_goodput + self.event_handler.request_completed_from_db_counter_for_badput)/self.simulation_time} reqs/sec

system goodput : {(self.event_handler.request_completed_from_system_for_goodput)/self.simulation_time} reqs/sec
app server goodput : {(self.event_handler.request_completed_from_app_counter_for_goodput)/self.simulation_time} reqs/sec
db server goodput : {(self.event_handler.request_completed_from_db_counter_for_goodput)/self.simulation_time} reqs/sec

system badput : {(self.event_handler.request_completed_from_system_for_badput)/self.simulation_time} reqs/sec
app server badput : {(self.event_handler.request_completed_from_app_counter_for_badput)/self.simulation_time} reqs/sec
db server badput : {(self.event_handler.request_completed_from_db_counter_for_badput)/self.simulation_time} reqs/sec

system average response time : {self.event_handler.average_response_time_of_system} sec
app server average response time : {self.event_handler.average_response_time_of_app_server} sec
db server average response time : {self.event_handler.average_response_time_of_db_server} sec

number in system : {self.event_handler.number_in_system}
number in app server : {self.event_handler.number_in_app_server}
number in db app server : {self.event_handler.number_in_db_server}

priority requests dropped : {self.event_handler.priority_request_dropped}
regular requests dropped : {self.event_handler.regular_request_dropped}
total requests served : {self.event_handler.request_completed_from_system_for_goodput + self.event_handler.request_completed_from_system_for_badput}
fraction of requests dropped : {round((self.event_handler.priority_request_dropped + self.event_handler.regular_request_dropped)/(self.event_handler.request_completed_from_system_for_goodput + self.event_handler.request_completed_from_system_for_badput + self.event_handler.priority_request_dropped + self.event_handler.regular_request_dropped),3)}

app server utilization : {self.event_handler.application_server.busy_cores/self.event_handler.application_server.core_count}
db server utlization: {self.event_handler.db_server.busy_cores/self.event_handler.db_server.core_count}
        """)