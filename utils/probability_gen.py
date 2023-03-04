import numpy as np


def get_probablity(prob):
    max_num = 10**4
    num = np.random.randint(low=1, high=max_num)
    if num <= prob * max_num:
        return True
    return False

def calculate_average_response_time(current_average, number_of_requests_served, new_response_time):
    return round((current_average*number_of_requests_served + new_response_time)/(number_of_requests_served + 1),3)

def calculate_number_in_the_server(server):
    return server.busy_cores + len(server.regular_queue) + len(server.priority_queue)