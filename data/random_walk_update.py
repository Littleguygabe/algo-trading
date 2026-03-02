import pandas as pd
import random
import os
import logging
from datetime import datetime

# Parameters
num_walks = 50
num_steps = 1000
output_dir = 'data/random_walk_data'
start_value = 100 # Start value for the walk
logging.basicConfig(level=logging.INFO)


# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(output_dir):
    file_path = os.path.join(output_dir, filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

# Generate a range of business days ending today
dates = pd.date_range(end=datetime.now(), periods=num_steps, freq='B')

for i in range(num_walks):
    # Generate random walk data
    steps = [start_value]
    current_value = start_value
    for _ in range(num_steps - 1):
        # Move up or down by a random amount between -1 and 1
        step = random.uniform(-1, 1)
        current_value += step
        steps.append(current_value)

    # Create a DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Close': steps
    })

    # Save to CSV
    file_path = os.path.join(output_dir, f'RW_{i+1}.csv')
    df.to_csv(file_path, index=False)

    logging.info(f"Saved {file_path}")

logging.info(f"Generated and saved {num_walks} random walks with synthetic dates.")
