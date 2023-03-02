class Request:
    def __init__(self, request_priority:int, request_timeout:float, need_server:int) -> None:
        """Instance of a web server request

        Args:
            request_priority (int): priority of request
            request_timeout (float): timeout value after which request is dropped
            need_server (int): server type
        """
        self.request_priority = request_priority
        self.request_timeout = request_timeout
        self.need_server = need_server