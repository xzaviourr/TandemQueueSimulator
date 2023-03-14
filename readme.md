# **DISCRETE EVENT SIMULATOR FOR PRIORITY TANDEM QUEUE**

Discrete Event Simulator for measuring characteristics of a custom web server modeled as a closed-loop tandem queuing system having **N** application server and **D** database instances in order to capture model behaviours.  

# System Design

![plot](./priority_tandem_queue_design.png)

# Running the simulator
- Run the code with the following command-line arguments: <br/>
 -<b>app_servers</b>: Number of application servers <br/>
 -<b>db_servers</b>: Number of database servers <br/>
 -<b>app_server_service_time</b>: Service time of application servers <br/>
 -<b>db_server_service_time</b>: Service time of database servers <br/>
 -<b>app_to_db_server_probability</b>: Probability of request going to database server from application server <br/>
 -<b>simulation_time</b>: Number of application servers <br/>
 -<b>num_client</b>: Number of application servers <br/>
 -<b>think_time</b>: Think time of client <br/>
 -<b>priority_probability</b>: Probability of request being a priority request <br/> <br/>
 - Command to run: <br/>
   `python --app_servers <app_servers> --db_servers <db_servers> --app_server_service_time <app_server_service_time> --db_server_service_time <db_server_service_time> --app_to_db_server_probability <app_to_db_server_probability> --simulation_time <simulation_time> --num_client <num_client> --think_time <think_time> --priority_probability <priority_probability>` <br/> <br/>
 - For instance: <br/>
    `python main.py --app_servers 2 --db_servers 2 --app_server_service_time 0.01 --db_server_service_time 0.1 --app_to_db_server_probability 0.3 --simulation_time 10 --num_client 10000 --think_time 5 --priority_probability 0.2`
