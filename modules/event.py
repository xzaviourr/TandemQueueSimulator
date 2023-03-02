from modules.request import Request


class Event:
    def __init__(self, type:int, request:Request, time:float) -> None:
        self.type = type
        self.request = request
        self.time = time

    def __lt__(self, other):
        return self.time < other.time
    
    def __str__(self):
        return f"{self.type} : {self.time}"