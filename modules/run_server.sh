#!/bin/bash

# for (( request_timeout=80 ; request_timeout>0; request_timeout=request_timeout-20 ))
for (( request_timeout=20 ; request_timeout>0; request_timeout=request_timeout-20 ))
do
    echo Request_Timeout: $request_timeout
    request_timeout_str=$(echo $request_timeout)
    # for (( num_users=1; num_users<=1501; num_users=num_users+20));
    for (( num_users=1401; num_users<=1501; num_users=num_users+20));
    # for num_users in {1..1000}
    do
        num_users_str=$(echo $num_users)
        echo Number_of_users: $num_users_str
        python main.py --app_servers 10 --db_servers 10 --app_server_service_time 0.1 --db_server_service_time 1 --app_to_db_server_probability 0.2 --simulation_time 100 --num_client $num_users_str --think_time 5 --priority_probability 0.2 --app_server_queue_length 1000 --db_server_queue_length 1000 --retry_delay 0.1 --request_timeout $request_timeout_str
    done
done