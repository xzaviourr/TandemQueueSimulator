import settings

import heapq
from typing import List

from modules.event import Event
from modules.server import Server
from modules.request import Request
from utils.probability_gen import get_probablity


class EventHandler:
    def __init__(self, event_queue:List[Event], application_server:Server, db_server:Server, app_to_db_prob:float, think_time:float, priority_prob:float) -> None:
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
        if event.type == settings.EVENT_REQUEST_ARRIVAL:    # When a request arrives at the application server
            if event.request.need_server == settings.APPLICATION_SERVER:    # arrived at application server
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
                                request_timeout = None,
                                need_server = settings.APPLICATION_SERVER
                            ),
                            time = current_time + self.think_time
                        )
                    )
                self.application_server.busy_cores -= 1
                self.request_completed_from_system += 1

            # Schedule next request
            if len(self.application_server.priority_queue) != 0:    # Priority request waiting
                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                        request = self.application_server.priority_queue.pop(0),
                        time = current_time + self.application_server.get_service_time()
                    )
                )
                self.application_server.busy_cores += 1

            elif len(self.application_server.regular_queue) != 0:   # Regular request waiting
                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                        request = self.application_server.regular_queue.pop(0),
                        time = current_time + self.application_server.get_service_time()
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
            if len(self.db_server.priority_queue) != 0:    # Priority request waiting
                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER,
                        request = self.db_server.priority_queue.pop(0),
                        time = current_time + self.db_server.get_service_time()
                    )
                )
                self.db_server.busy_cores += 1

            elif len(self.db_server.regular_queue) != 0:   # Regular request waiting
                heapq.heappush(
                    self.event_queue, 
                    Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER,
                        request = self.db_server.regular_queue.pop(0),
                        time = current_time + self.db_server.get_service_time()
                    )
                )
                self.db_server.busy_cores += 1