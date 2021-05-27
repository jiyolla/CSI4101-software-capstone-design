class ServerState:
    def __init__(self, region, name, ip, port, models, available_cpu, available_gpu, available_mem, network_usage):
        self.region = region
        self.name = name
        self.ip = ip
        self.port = port
        self.address = f'{ip}:{port}'
        self.models = models'available_models': 'should be scanned automatically',
        
        
    @classmethod
    def empty_state(cls):
        return [0, 0, 0, 0]

    def to_state(self):
        return [self.region, self.image_size, self.expected_time.total_seconds(), self.expected_accuracy]
