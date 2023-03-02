import settings

import heapq
from typing import List

from modules.event import Event
from modules.server import Server


class EventHandler:
    def __init__(self, event_queue:List[Event], application_server:Server, db_server:Server) -> None:
        self.application_server = application_server
        self.db_server = db_server
        self.event_queue = event_queue

    def handle_event(self, event:Event):
        if event.type == settings.EVENT_REQUEST_ARRIVAL:    # When a request arrives at the application server
            if event.request.need_server == settings.APPLICATION_SERVER:    # arrived at application server
                if self.application_server.busy_cores < self.application_server.core_count:  # cores are available
                    heapq.heappush(self.event_queue, Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER,
                        request = event.request
                    ))
                    self.application_server.busy_cores += 1
                else:
                    if event.request.request_priority == settings.HIGH_PRIORITY:
                        self.application_server.priority_queue.append(event.request) 
                    else:
                        self.application_server.regular_queue.append(event.request)
                    
            else:   # arrived at db server
                if self.db_server.busy_cores < self.db_server.core_count:   # cores are available
                    heapq.heappush(self.event_queue, Event(     # Start processing the event
                        type = settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER,
                        request = event.request
                    ))
                    self.db_server.busy_cores += 1
                else:
                    if event.request.request_priority == settings.HIGH_PRIORITY:
                        self.db_server.priority_queue.append(event.request) 
                    else:
                        self.db_server.regular_queue.append(event.request)

        elif event.type == settings.EVENT_REQUEST_COMPLETE_FROM_APP_SERVER:
            pass

        elif event.type == settings.EVENT_REQUEST_COMPLETE_FROM_DB_SERVER:
            pass