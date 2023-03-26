#!/bin/bash

for db_call_type in 1 0
do
    db_call_is_synchronous_str=$(echo $db_call_type)
    request_timeout_str=$(echo $request_timeout)
    for (( num_users=1; num_users<=1451; num_users=num_users+50));
    do
        num_users_str=$(echo $num_users)
        echo Number_of_users: $num_users_str
        python main.py --app_servers 20 --db_servers 5 --app_server_service_time 0.1 --db_server_service_time 1 --app_to_db_server_probability 0.02 --simulation_time 600 --num_client $num_users_str --think_time 5 --priority_probability 0.2 --app_server_queue_length 1000 --db_server_queue_length 1000 --retry_delay 0.1 --db_call_is_synchronous $db_call_is_synchronous_str --request_timeout 20
    done
done