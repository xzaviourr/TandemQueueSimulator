from modules.request import Request


class Event:
    def __init__(self, type:int, request:Request, time:float) -> None:
        self.type = type
        self.request = request
        self.time = time

    def __lt__(self, other):
        return self.time < other.time
    
    def __str__(self):
        if self.type == 1:
            return f"EVENT_REQUEST_ARRIVAL : {self.request.id} : {self.time}"
        elif self.type == 2:
            return f"EVENT_REQUEST_COMPLETE_FROM_APP_SERVER : {self.request.id} : {self.time}"
        else:
            return f"EVENT_REQUEST_COMPLETE_FROM_DB_SERVER : {self.request.id} : {self.time}"