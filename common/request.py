from datetime import datetime, timedelta
import os
import sys
import imagesize
import numpy as np


class Request:
    def __init__(self, unique_id, region, image_id, accuracy, time):
        self.unique_id = unique_id
        self.region = region
        self.image_id = image_id
        self.image_path = os.path.join(sys.path[0], f'../data/image/{image_id}.JPEG')
        self.expected_accuracy = accuracy
        self.expected_time = timedelta(seconds=time)
        self.image_size = np.prod(imagesize.get(self.image_path))
        self.timestamps = {
            'Created': datetime.now(),
            'Allocated': None,
            'Preprocessed': None,
            'Served': None
        }

    @classmethod
    def empty_state(cls):
        return [0, 0, 0, 0]

    def to_state(self):
        return [self.region, self.image_size, self.expected_time.total_seconds(), self.expected_accuracy]

    def set_allocated(self, server):
        self.timestamps['Allocated'] = datetime.now()
        self.served_by = server

    def set_preprocessed(self):
        self.timestamps['Preprocessed'] = datetime.now()

    def set_served(self, response):
        self.timestamps['Served'] = datetime.now()
        self.response = response
        self.elapsed_time = self.timestamps['Served'] - self.timestamps['Allocated']
