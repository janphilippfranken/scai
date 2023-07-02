
#%%
import pandas as pd

data = pd.read_csv('sim_res/sim_1/0/sim_1_0_user.csv')
data
print('running')



x = 'epoch'
y = 'satisfaction'
z = 'agent_id'
grouping = 'agent_id'
user_data = {}
user_data[x] = list(data[x])
user_data[y] = list(data[y])
user_data[z] = list(data[z])
print(user_data)
print(len(data['agent_id'].unique()))

from plots import plot_user_data

plot_user_data(user_data)


# %%
