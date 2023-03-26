# **DISCRETE EVENT SIMULATOR FOR SYNCHRONOUS / ASYNCHRONOUS PRIORITY TANDEM QUEUE**

Discrete Event Simulator for measuring characteristics of a custom web server modeled as a closed-loop tandem queuing system having **N** application server and **D** database instances in order to capture model behaviours.  

## **System Design**

![plot](./priority_tandem_queue_design.png)

## **Installation**
- Clone the repository

    ```git clone https://github.com/xzaviourr/TandemQueueSimulator.git```

- Create virtual environment

    ```python3 -m venv venv```

- Install python dependencies

    ```pip install -r requirements.txt```

## **Running the simulator**
- Run the code with the following command-line arguments: <br/>
 -<b>app_servers</b>: Number of application servers <br/>
 -<b>db_servers</b>: Number of database servers <br/>
 -<b>app_server_service_time</b>: Service time of application servers <br/>
 -<b>db_server_service_time</b>: Service time of database servers <br/>
 -<b>app_to_db_server_probability</b>: Probability of request going to database server from application server <br/>
 -<b>simulation_time</b>: Number of application servers <br/>
 -<b>num_client</b>: Number of application servers <br/>
 -<b>think_time</b>: Think time of client <br/>
 -<b>priority_probability</b>: Probability of request being a priority request <br/>
 -<b>app_server_queue_length</b>: Buffer queue length of the app server <br/>
 -<b>db_server_queue_length</b>: Buffer queue length of the db server <br/>
 -<b>retry_delay</b>: Retry time after request is dropped from the server <br/>
 -<b>request_timeout</b>: Request timeout duration <br/>
 -<b>db_call_is_synchronous_str</b>: Choose for synchronous or asynchronous <br/> <br/>

 - Command to run: <br/>
   `python --app_servers <app_servers> --db_servers <db_servers> --app_server_service_time <app_server_service_time> --db_server_service_time <db_server_service_time> --app_to_db_server_probability <app_to_db_server_probability> --simulation_time <simulation_time> --num_client <num_client> --think_time <think_time> --priority_probability <priority_probability> --app_server_queue_length <buffer queue length> --db_server_queue_length <buffer queue lenght> --retry_delay <retry time after timeout> --request_timeout <request_timeout> --db_call_is_synchronous_str <async or sync>` <br/> <br/>
 - For instance: <br/>
    `python main.py --app_servers 2 --db_servers 2 --app_server_service_time 0.01 --db_server_service_time 0.1 --app_to_db_server_probability 0.3 --simulation_time 10 --num_client 10000 --think_time 5 --priority_probability 0.2 --app_server_queue_length 1000 --db_server_queue_lenght 1000 --retry_delay 0.1 --request_timeout 80 --db_call_is_synchronous_str 1`