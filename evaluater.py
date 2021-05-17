# 1. Read Training data
# 2. Listen to response from controller.py
# 3. Evaluate avg.
import pandas as pd

df = pd.read_csv('data/LOC_val_solution.csv')


def evaluate(metadata_req, res):
    # Time measurement
    time = metadata_req['timestamps']['served'] - metadata_req['timestamps']['accepted']
    print(time)

    # Accuracy
    is_correct = res in df[df['ImageId'] == metadata_req['image_id']]['PredictionString'].to_string()
    print(is_correct)
    return time, is_correct
