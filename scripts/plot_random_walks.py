import pandas as pd
import matplotlib.pyplot as plt
import os

if __name__ == '__main__':
    data_dir = './data/random_walk_data'
    final_positions = []

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), sharey=True, 
                               gridspec_kw={'width_ratios': [3, 1]})

    for filename in os.listdir(data_dir):
        data = pd.read_csv(f'{data_dir}/{filename}')
        final_positions.append(data.iloc[-1]['Close'])
        ax1.plot(data,color='grey',alpha=0.2)

    ax2.hist(final_positions, bins=25, orientation='horizontal', 
            color='royalblue', edgecolor='white')
    print(final_positions)
    plt.tight_layout()
    plt.show()