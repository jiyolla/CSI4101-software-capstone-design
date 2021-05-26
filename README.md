## A network-aware load balancer using DRL

### Scenario:
1. Clients send request to an edge server and the request metadata to DRL load balancer.
2. DRL load balancer decide where the request should actually be handled and send the control message to serving servers.
3. Serving server enqueue client request and either transfer or handle requests upon DRL load balancer's command.


### Scenario with emulator:
1. ".
2. ". The network bandwidth of each server is artificially compromised.
3. ". Request transfer between serving servers is delayed accoridngly.


### Things To D
1. Make emulator switchable. That is the entire project could work without emulator if all clients/servers are properly set.
2. Overhaul the content and structure of 'server_states'
3. Implement DRL and tune it.

4. Objectize(Class) request metadata. There are some specific 'methods' involved with those data.
5. Include dockerfile of the service server to automate deployment. Also probably include some bash command for multiple docker each serving a single model.

**client.py:**  
1. Load ImageNet validation images.
2. Query loadbalancer.py for inferencing server address.
3. Send request to inferencing server.
4. Calculate artficial network overhead.
5. Send result to evaluater.py.

**loadbalancer.py:**  
1. Generate 'oberservation' for DRL upon client query for serving address.
2. Return DRL's action(serving address) to client.

**evaluater.py:**  
1. Load ImageNet validation solutions.
2. Identify request and rate correspoding service response by accuracy&time.

**reportmonitor.py:**  
1. Collect server's state.
2. Send it to servermonitor.py.

**DRL.py:**  
Not considred yet.
