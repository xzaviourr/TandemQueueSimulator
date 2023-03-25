import settings

import heapq
from typing import List
import logging

from modules.event import Event
from modules.server import Server
from modules.request import Request
from utils.probability_gen import get_probablity, calculate_average_response_time, calculate_number_in_the_server, get_retry_delay


class EventHandler:
    def __init__(self, event_queue:List[Event], application_server:Server, db_server:Server, app_to_db_prob:float, 
                 think_time:float, priority_prob:float, logger:logging.Logger, app_server_queue_length:int, 
                 db_server_queue_length:int, retry_delay:float, request_timeout:int) -> None:
        """Instance of event handler for the simulator

        Args:
            event_queue (List[Event]): Event queue for the simulator
            application_server (Server): Application server instance
            db_server (Server): Db server instance
            app_to_db_prob (float): Probability request will go from app server to db server
            think_time (float): think time of the users
            priority_prob (float): probability that request is of high probability 
            logger (logging.Logger): Logger object
            app_server_queue_length (int): Maximum length of waiting queue of app server
            db_server_queue_length (int): Maximum lenght of waiting queue of db server
            retry_delay (float): Retry sending packet after failure
            request_timeout (float): Timeout value for requests
        """
        self.logger = logger
        
        self.application_server = application_server
        self.db_server = db_server
        self.event_queue = event_queue
        self.app_to_db_prob = app_to_db_prob
        self.think_time = think_time
        self.priority_prob = priority_prob
        self.app_server_queue_length = app_server_queue_length
        self.db_server_queue_length = db_server_queue_length
        self.retry_delay = retry_delay
        self.request_timeout = request_timeout

        self.request_dropped_dict = {}
        self.request_completed_dict = {}

        self.request_completed_from_app_counter_for_goodput = 0
        self.request_completed_from_db_counter_for_goodput = 0
        self.request_completed_from_system_for_goodput = 0

        self.request_completed_from_app_counter_for_badput = 0
        self.request_completed_from_db_counter_for_badput = 0
        self.request_completed_from_system_for_badput = 0

        self.priority_request_dropped = 0
        self.regular_request_dropped = 0

        self.average_response_time_of_system = 0
        self.average_response_time_of_app_server = 0
        self.average_response_time_of_db_server = 0
        
        self.number_in_app_server = calculate_number_in_the_server(self.application_server)
        self.number_in_db_server = calculate_number_in_the_server(self.db_server)
        self.number_in_system = self.number_in_app_server + self.number_in_db_server

    def push_in_queue(self, event:Event, server:Server, queue_length:int, current_time:float):
        """Pushes event in queue

        Args:
            event (Event): Event to be served
            server (Server): Application or Db server
            queue_length (int): Max queue length
            current_time (float): Current time
        """
        if event.request.request_priority == settings.HIGH_PRIORITY:
            if len(server.priority_queue) < queue_length:
                server.priority_queue.append(event.request)
            else:
                self.handle_event_timeout(event, current_time)  # Request dropped due to queue overflow
        else:
            if len(server.regular_queue) < queue_length:
                server.regular_queue.append(event.request)
            else:
                self.handle_event_timeout(event, current_time)  # Request dropped due to queue overflow

    def handle_event_request_arrival(self, event:Event, current_time:float):
        """Event generated when request arrives at the application server

        Args:
            event (Event): Event to be handled
            current_time (float): current time of the simulation
        """
        heapq.heappush(
            self.event_queue, 
            Event(     # Timout event
                type = settings.EVENT_TIMEOUT,
                request = event.request,
                time = current_time + self.request_timeout
            )
        )

        if self.application_server.busy_cores < self.application_server.core_count:  # cores are available
            heapq.heappush(
                self.event_queue, 
                Event(     # Start processing the event
                    type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                    request = event.request,
                    time = current_time + self.application_server.get_service_time()
                )
            )
            self.application_server.busy_cores += 1

        else:
            self.push_in_queue(event, self.application_server, self.app_server_queue_length, current_time)
        
        self.number_in_app_server = calculate_number_in_the_server(self.application_server)
        self.number_in_db_server = calculate_number_in_the_server(self.db_server)
        self.number_in_system = self.number_in_app_server + self.number_in_db_server

    def handle_event_request_complete_from_app_server(self, event:Event, current_time:float):
        """Event handled when request gets completed from the app server

        Args:
            event (Event): Event to be handled
            current_time (float): current time of the simulation
        """
        if not event.request.id in self.request_dropped_dict.keys():
            response_time = current_time - event.request.arrival_time
            self.average_response_time_of_app_server = calculate_average_response_time(self.average_response_time_of_app_server, (self.request_completed_from_app_counter_for_goodput + self.request_completed_from_app_counter_for_badput), response_time)
            if event.request.is_timed_out:
                self.request_completed_from_app_counter_for_badput += 1
            else:
                self.request_completed_from_app_counter_for_goodput += 1
            
            if get_probablity(self.app_to_db_prob): # Request moves to db
                if self.db_server.busy_cores < self.db_server.core_count:   # Request goes to processing
                    heapq.heappush(
                        self.event_queue,
                        Event(
                            type = settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER,
                            request = event.request,
                            time = current_time + self.db_server.get_service_time()
                        )
                    )
                    self.db_server.busy_cores += 1

                else:   # Request moves to queue
                    self.push_in_queue(event, self.db_server, self.db_server_queue_length, current_time)

                if not settings.SYNCHRONIZE:
                    self.application_server.busy_cores -= 1

            else:   # Request completed
                self.request_completed_dict[event.request.id] = 1
                heapq.heappush(
                        self.event_queue,
                        Event(
                            type = settings.EVENT_REQUEST_ARRIVAL,
                            request = Request(
                                request_priority = int(get_probablity(self.priority_prob)),
                                request_timeout = self.request_timeout,
                                need_server = settings.APPLICATION_SERVER,
                                arrival_time = current_time + self.think_time
                            ),
                            time = current_time + self.think_time
                        )
                    )
                self.application_server.busy_cores -= 1    
                response_time = (current_time - event.request.arrival_time)
                self.average_response_time_of_system = calculate_average_response_time(self.average_response_time_of_system, (self.request_completed_from_system_for_goodput + self.request_completed_from_system_for_badput), response_time)
                if event.request.is_timed_out:
                    self.request_completed_from_system_for_badput += 1
                else:
                    self.request_completed_from_system_for_goodput += 1
        
        else:
            self.application_server.busy_cores -= 1            

        # Schedule next request
        while True:
            if len(self.application_server.priority_queue) != 0:    # Priority request waiting
                new_request = self.application_server.priority_queue.pop(0)

            elif len(self.application_server.regular_queue) != 0:   # Regular request waiting
                new_request = self.application_server.regular_queue.pop(0)

            else:   # No request available for scheduling
                break

            if new_request.id not in self.request_dropped_dict.keys():
                after_service_time = current_time + self.application_server.get_service_time()

                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                        request = new_request,
                        time = after_service_time
                    )
                )
                self.application_server.busy_cores += 1
                break
        
        self.number_in_app_server = calculate_number_in_the_server(self.application_server)
        self.number_in_db_server = calculate_number_in_the_server(self.db_server)
        self.number_in_system = self.number_in_app_server + self.number_in_db_server

    def handle_event_request_complete_from_db_server(self, event:Event, current_time:float):
        """Event handled when request processing is completed from the db server

        Args:
            event (Event): Event to be handled
            current_time (float): current simulation time
        """
        if event.request.id not in self.request_dropped_dict.keys():
            response_time = current_time - event.request.arrival_time
            self.average_response_time_of_db_server = calculate_average_response_time(self.average_response_time_of_db_server, (self.request_completed_from_db_counter_for_goodput + self.request_completed_from_db_counter_for_badput), response_time)
            if event.request.is_timed_out:
                self.request_completed_from_db_counter_for_badput += 1
            else:
                self.request_completed_from_db_counter_for_goodput += 1
            
            self.db_server.busy_cores -= 1
            if self.application_server.busy_cores < self.application_server.core_count:  # cores are available
                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                        request = event.request,
                        time = current_time + self.application_server.get_service_time()
                    )
                )
                if not settings.SYNCHRONIZE:
                    self.application_server.busy_cores += 1
            else:
                self.push_in_queue(event, self.application_server, self.app_server_queue_length, current_time)
        else:
            self.db_server.busy_cores -= 1

        # Schedule new request
        while True:
            if len(self.db_server.priority_queue) != 0:    # Priority request waiting
                new_request = self.db_server.priority_queue.pop(0)
            elif len(self.db_server.regular_queue) != 0:   # Regular request waiting
                new_request = self.db_server.regular_queue.pop(0)
            else:   # No request available for scheduling
                break

            if new_request.id not in self.request_dropped_dict.keys():
                after_service_time = current_time + self.db_server.get_service_time()

                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER,
                        request = new_request,
                        time = after_service_time
                    )
                )
                self.db_server.busy_cores += 1
                break
    
        self.number_in_app_server = calculate_number_in_the_server(self.application_server)
        self.number_in_db_server = calculate_number_in_the_server(self.db_server)
        self.number_in_system = self.number_in_app_server + self.number_in_db_server

    def handle_event_timeout(self, event:Event, current_time:float, is_timeout:bool=False):
        """Event handled when timeout is raised or buffer queue is full

        Args:
            event (Event): Event to be handled
            current_time (float): current time of the simulation
        """
        self.logger.critical(f"REQUEST_DROPPED : {event.request.id} : {current_time}")
        if event.request.request_priority == settings.HIGH_PRIORITY:
            self.priority_request_dropped += 1
        else:
            self.regular_request_dropped += 1

        self.request_dropped_dict[event.request.id] = 1

        if not is_timeout:
            heapq.heappush(
            self.event_queue,
            Event(
                type = settings.EVENT_REQUEST_ARRIVAL,
                request = Request(
                    request_priority = event.request.request_priority,
                    request_timeout = self.request_timeout,
                    need_server = settings.APPLICATION_SERVER,
                    arrival_time = current_time + get_retry_delay(self.retry_delay) 
                ),
                time = current_time + get_retry_delay(self.retry_delay) 
                )
            )
        else:
            heapq.heappush(
            self.event_queue,
            Event(
                type = settings.EVENT_REQUEST_ARRIVAL,
                request = Request(
                    request_priority = event.request.request_priority,
                    request_timeout = self.request_timeout,
                    need_server = settings.APPLICATION_SERVER,
                    arrival_time = current_time + get_retry_delay(self.retry_delay),
                    is_timed_out = True 
                ),
                time = current_time + get_retry_delay(self.retry_delay) 
                )
            )

    def handle_event(self, event:Event, current_time:float):
        """Event handle function

        Args:
            event (Event): Event object
            current_time (float): simulation time
        """
        self.logger.critical(event)
        if event.type == settings.EVENT_REQUEST_ARRIVAL:    # When a request arrives at the application server
            self.handle_event_request_arrival(event=event, current_time=current_time)

        elif event.type == settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER:
                self.handle_event_request_complete_from_app_server(event=event, current_time=current_time)

        elif event.type == settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER:
                self.handle_event_request_complete_from_db_server(event=event, current_time=current_time)

        elif event.type == settings.EVENT_TIMEOUT:
            if event.request.id not in self.request_completed_dict.keys():  # Completed
                self.handle_event_timeout(event=event, current_time=current_time, is_timeout=True)