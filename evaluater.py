# 1. Read Training data
# 2. Listen to response from controller.py
# 3. Evaluate avg.
import pandas as pd

df = pd.read_csv('data/LOC_val_solution.csv')


def evaluate(metadata_req, res):
    # Time requirement
    elapsed_time = metadata_req['timestamps']['served'] - metadata_req['timestamps']['accepted']
    is_timely = metadata_req['requirement']['time'] >= elapsed_time
    print(f'Elapsed time: {elapsed_time}')
    print(f'Expected time: {metadata_req["requirement"]["time"]}')
    print(f'is_timely: {is_timely}')

    # Accuracy requirement
    is_correct = res in df[df['ImageId'] == metadata_req['image_id']]['PredictionString'].to_string()
    print(f'Image Id: {metadata_req["image_id"]}')
    print(f'Ground truth: {df[df["ImageId"] == metadata_req["image_id"]]["PredictionString"].to_string()}')
    print(f'Prediction: {res}')
    print(f'is_correct: {is_correct}')
    return is_timely, is_correct
