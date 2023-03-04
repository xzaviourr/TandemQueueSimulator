import settings

import heapq
from typing import List
import logging

from modules.event import Event
from modules.server import Server
from modules.request import Request
from utils.probability_gen import get_probablity


class EventHandler:
    def __init__(self, event_queue:List[Event], application_server:Server, db_server:Server, app_to_db_prob:float, 
                 think_time:float, priority_prob:float, logger:logging.Logger) -> None:
        self.logger = logger
        
        self.application_server = application_server
        self.db_server = db_server
        self.event_queue = event_queue
        self.app_to_db_prob = app_to_db_prob
        self.think_time = think_time
        self.priority_prob = priority_prob

        self.request_completed_from_app_counter = 0
        self.request_completed_from_db_counter = 0
        self.request_completed_from_system = 0

    def handle_event(self, event:Event, current_time:float):
        self.logger.critical(event)
        if event.type == settings.EVENT_REQUEST_ARRIVAL:    # When a request arrives at the application server
            if event.request.need_server == settings.APPLICATION_SERVER:    # arrived at application server
                if self.application_server.busy_cores < self.application_server.core_count:  # cores are available
                    
                    after_service_time = current_time + self.application_server.get_service_time()
                    if event.request.request_timeout + event.request.arrival_time < after_service_time:     # Timeout condition
                        self.logger.critical(f"REQUEST_DROPPED : {event.request.id} : {current_time}")
                        
                        heapq.heappush(
                        self.event_queue,
                        Event(
                            type = settings.EVENT_REQUEST_ARRIVAL,
                            request = Request(
                                request_priority = int(get_probablity(self.priority_prob)),
                                request_timeout = settings.REQUEST_TIMEOUT,
                                need_server = settings.APPLICATION_SERVER,
                                arrival_time = current_time
                            ),
                            time = current_time
                            )
                        )
                        
                        return
                    
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
                    if event.request.request_priority == settings.HIGH_PRIORITY:
                        self.application_server.priority_queue.append(event.request) 
                    else:
                        self.application_server.regular_queue.append(event.request)

        elif event.type == settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER:
            self.request_completed_from_app_counter += 1

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
                    if event.request.request_priority == settings.HIGH_PRIORITY:
                        self.db_server.priority_queue.append(event.request) 
                    else:
                        self.db_server.regular_queue.append(event.request)

                self.application_server.busy_cores -= 1

            else:   # Request completed
                heapq.heappush(
                        self.event_queue,
                        Event(
                            type = settings.EVENT_REQUEST_ARRIVAL,
                            request = Request(
                                request_priority = int(get_probablity(self.priority_prob)),
                                request_timeout = settings.REQUEST_TIMEOUT,
                                need_server = settings.APPLICATION_SERVER,
                                arrival_time = current_time + self.think_time
                            ),
                            time = current_time + self.think_time
                        )
                    )
                self.application_server.busy_cores -= 1
                self.request_completed_from_system += 1

            # Schedule next request
            while True:
                if len(self.application_server.priority_queue) != 0:    # Priority request waiting
                    new_request = self.application_server.priority_queue.pop(0)

                elif len(self.application_server.regular_queue) != 0:   # Regular request waiting
                    new_request = self.application_server.regular_queue.pop(0)

                else:   # No request available for scheduling
                    break

                after_service_time = current_time + self.application_server.get_service_time()
                if new_request.arrival_time + new_request.request_timeout < after_service_time:     # Timeout condition
                    
                    self.logger.critical(f"REQUEST_DROPPED : {event.request.id} : {current_time}")
                        
                    heapq.heappush(
                    self.event_queue,
                    Event(
                        type = settings.EVENT_REQUEST_ARRIVAL,
                        request = Request(
                            request_priority = int(get_probablity(self.priority_prob)),
                            request_timeout = settings.REQUEST_TIMEOUT,
                            need_server = settings.APPLICATION_SERVER,
                            arrival_time = current_time
                        ),
                        time = current_time
                        )
                    )
                    continue

                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                        request = new_request,
                        time = after_service_time
                    )
                )
                self.application_server.busy_cores += 1

        elif event.type == settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER:
            self.request_completed_from_db_counter += 1
            
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
                self.application_server.busy_cores += 1
            else:
                if event.request.request_priority == settings.HIGH_PRIORITY:
                    self.application_server.priority_queue.append(event.request) 
                else:
                    self.application_server.regular_queue.append(event.request)

            # Schedule new request
            while True:
                if len(self.db_server.priority_queue) != 0:    # Priority request waiting
                    new_request = self.db_server.priority_queue.pop(0)
                elif len(self.db_server.regular_queue) != 0:   # Regular request waiting
                    new_request = self.db_server.regular_queue.pop(0)
                else:   # No request available for scheduling
                    break

                after_service_time = current_time + self.db_server.get_service_time()
                if new_request.arrival_time + new_request.request_timeout < after_service_time:     # Timeout condition
                    
                    self.logger.critical(f"REQUEST_DROPPED : {event.request.id} : {current_time}")
                        
                    heapq.heappush(
                    self.event_queue,
                    Event(
                        type = settings.EVENT_REQUEST_ARRIVAL,
                        request = Request(
                            request_priority = int(get_probablity(self.priority_prob)),
                            request_timeout = settings.REQUEST_TIMEOUT,
                            need_server = settings.APPLICATION_SERVER,
                            arrival_time = current_time
                        ),
                        time = current_time
                        )
                    )
                    
                    continue

                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER,
                        request = new_request,
                        time = after_service_time
                    )
                )
                self.db_server.busy_cores += 1