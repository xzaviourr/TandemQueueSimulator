from modules.request import Request


class Event:
    def __init__(self, type:int, request:Request, time:float) -> None:
        self.type = type
        self.request = request
        self.time = time