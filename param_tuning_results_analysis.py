import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import scatter_matrix 

# Opening the file
tuning_results_file_path = "param_tuning_results.csv"
df = pd.read_csv(tuning_results_file_path)

df["error_rate"].hist()
# scatter_matrix(df)

plt.show()

# corr_matrix = df.corr()
# print(corr_matrix["error_rate"].sort_values(ascending=False))

