## A network-aware load balancer using DRL



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
