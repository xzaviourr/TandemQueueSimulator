import numpy as np


def get_probablity(prob):
    """Select item from probabilistic distribution

    Args:
        prob (float): Probability of event A

    Returns:
        bool: True for event A, False for event B
    """
    max_num = 10**4
    num = np.random.randint(low=1, high=max_num)
    if num <= prob * max_num:
        return True
    return False

def calculate_average_response_time(current_average, number_of_requests_served, new_response_time):
    """Average response time 

    Args:
        current_average (float): Current running average
        number_of_requests_served (int): Number of requests served
        new_response_time (float): New response time to add to the average

    Returns:
        float : New average
    """
    return round((current_average*number_of_requests_served + new_response_time)/(number_of_requests_served + 1),3)

def calculate_number_in_the_server(server):
    """Total number of request in the server

    Args:
        server (Server): Server object

    Returns:
        int: Number of requests in the server
    """
    return server.busy_cores + len(server.regular_queue) + len(server.priority_queue)