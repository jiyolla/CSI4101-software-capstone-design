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

**client_req.py:**  
1. Load ImageNet validation images
2. Generate paremeterized(request interval, expected accuracy/time, etc) request distribution

**emulator.py:**  
1. Handle client request  
    1. Collect request meta-info and server states info
    2. Send them to DRL server to decide which (server:service) to use.
    3. Listen for DRL server's response(action).
    4. Make the actual service request while emulating network overhead.
2. Monitor server states
    1. Collect server states from each server and make them send-ready.
3. Emulate networking between servers.
    1. Interface to control/paremeterize network overhead
    2. Emulate delayed/limited transfer
    3. Emulate server states(only networking stats)

**evaluater.py:**  
1. Load ImageNet validation solutions.
2. Identify request and rate correspoding service response by accuracy&time.

**server_monitor.py:**  
1. Collect server's state.
2. Send it to emulator.

**DRL.py:**  
Not considred yet.
