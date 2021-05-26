## A network-aware load balancer using DRL

### Scenario:
1. Client query load balancing server for inferencing server address.
2. Load balancer return serving address using DRL.
3. Client send actual request to inferencing server.
4. Add artifical network overhead upon receiving inferencing response.
5. Return overall results to evaluater to generate reward for DRL.


### Things To Do
1. Implement DRL and tune it.

2. Automate deployment.
    1. Include dockerfile of the service server. Also probably include some bash command for multiple docker each serving a single model.
    2. Scripts to install prerequisite.

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
2. Listen from client response reports and parse feed to drl.py

**servermonitor.py**  
1. Listen for state reports from servermonitor.py
2. Send gathered state reports to drl.py

**reportstate.py:**  
1. Collect server's state.
2. Send it to servermonitor.py.

**drl.py:**  
1. Uses request and server_state as state
2. DQN to aprox. q function
3. Return server/model as action