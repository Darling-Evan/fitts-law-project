import uuid
import csv
import random

def generate_participant_id():
    return str(uuid.uuid4())[:8]

def generate_trial_sequence():
    configs = list(range(18)) * 10
    random.shuffle(configs)
    return configs

def save_trial_data(participant_id, trial_data):
    filename = f"data/participant_{participant_id}.csv"
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Trial", "Distance", "Size", "Direction", "Time(ms)", "MouseDist", "Errors"])
        writer.writerows(trial_data)
