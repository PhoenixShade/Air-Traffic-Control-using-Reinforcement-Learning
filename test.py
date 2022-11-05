import numpy as np
import pickle
with open("Q_table_e_greedy.pickle", 'rb') as f:
    Q_table = pickle.load(f)
print(Q_table)