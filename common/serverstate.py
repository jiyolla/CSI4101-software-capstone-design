class ServerState:
    def __init__(self, region, name, ip, port, models, available_cpu, available_gpu, available_mem, network_usage):
        self.region = region
        self.name = name
        self.ip = ip
        self.port = port
        self.address = f'{ip}:{port}'
        self.models = models
        self.available_cpu = available_cpu
        self.available_gpu = available_gpu
        self.available_mem = available_mem
        self.network_usage = network_usage

    def __repr__(self):
        return f'{self.region}, {self.name}, {self.ip}, {self.port}, {self.models}, {self.available_cpu}'

    def to_state(self):
        return [self.region, self.available_cpu, self.available_gpu, self.available_mem, self.network_usage]
