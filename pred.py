import fastf1 as ff1
from fastf1 import plotting
from fastf1.ergast import Ergast
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report
from sklearn.preprocessing import MinMaxScaler
import warnings
import numpy as np
import scipy.special

warnings.filterwarnings('ignore')
ff1.Cache.enable_cache('cache_dir')

completed_rounds = [
    'Australia', 'China', 'Japan', 'Bahrain', 'Saudi Arabia', 'Miami', 'Emilia-Romagna', 'Monaco', 'Spain'
]

races_2025 = []
for gp in completed_rounds:
    try:
        session = ff1.get_session(2025, gp, 'R')
        session.load()
        df_gp = session.results
        df_gp['GrandPrix'] = gp
        races_2025.append(df_gp)
    except Exception as e:
        print(f'Failed to load {gp}: {e}')

df_2025 = pd.concat(races_2025, ignore_index=True)
df_2025['DriverNumber'] = df_2025['DriverNumber'].astype(int)
df_2025['won'] = (df_2025['Position'] == 1).astype(int)

driver_stats = df_2025.groupby('DriverNumber').agg({
    'Position': ['mean', 'min', 'max'],
    'Points': 'sum',
    'won': 'sum',
    'GridPosition': 'mean',
    'TeamName': 'last',
    'Abbreviation': 'last'
}).reset_index()

driver_stats.columns = [
    'DriverNumber', 'avg_pos', 'best_pos', 'worst_pos', 'total_points', 'wins', 'avg_grid', 'TeamName', 'Abbreviation'
]

df_train = df_2025.merge(driver_stats, on = 'DriverNumber', how = 'left')
features = [
    'avg_pos', 'best_pos', 'worst_pos', 'total_points', 'wins', 'avg_grid'
]

X_train = df_train[features]
#Y_train = df_train['won']
y_win = df_train['won']
y_position = df_train['Position']

win_clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
win_clf.fit(X_train, y_win)

#pos_reg = RandomForestClassifier(n_estimators=100, random_state=42)
pos_reg = RandomForestRegressor(n_estimators=100, random_state=42)
pos_reg.fit(X_train, y_position)

X_predict = driver_stats[features]
driver_stats['win_prob'] = win_clf.predict_proba(X_predict)[:, 1]
driver_stats['predicted_pos'] = pos_reg.predict(X_predict)

scaler = MinMaxScaler()
driver_stats['scaled_win_prob'] = scipy.special.softmax(driver_stats['win_prob'])
#driver_stats['scaled_win_prob'] = scaler.fit_transform(driver_stats[['win_prob']])
#driver_stats['norm_win_prob'] = np.exp(driver_stats['win_prob'] / np.sum(np.exp(driver_stats['win_prob'])))
win_output = driver_stats[['Abbreviation', 'scaled_win_prob']].sort_values(by='scaled_win_prob', ascending = False)
driver_stats['predicted_pos'] = driver_stats['predicted_pos'].clip(1, 20)
#top_10_output = driver_stats[['Abbreviation', 'predicted_pos']].sort_values(by='predicted_pos').head(10)
top_10_output = (
    driver_stats[['Abbreviation', 'predicted_pos']].sort_values(by='predicted_pos').reset_index(drop=True)
)
top_10_output['predicted_pos'] = top_10_output.index + 1
top_10_output = top_10_output.head(10)

print('\n Predicted winner probabilities for Canadian GP: \n')
print(win_output.to_string(index=False, float_format='%.3f'))

print('\n Predicted top 10 for the Canadian GP: \n')
print(top_10_output.to_string(index=False, float_format='%.2f'))

#import matplotlib.pyplot as plt

# top_probs = driver_stats.sort_values(by='scaled_win_prob', ascending=False).head(10)
# plt.figure(figsize=(10, 5))
# plt.bar(top_probs['Abbreviation'], top_probs['scaled_win_prob'], color='royalblue')
# plt.title('Top 10 Win Probabilities - Canadian GP')
# plt.xlabel('Driver')
# plt.ylabel('Win Probability')
# plt.ylim(0, 1.1)
# plt.grid(True, linestyle='--', alpha=0.5)
# plt.show()


#X_predict = driver_stats[[
#    'avg_pos', 'best_pos', 'worst_pos', 'total_points', 'wins', 'avg_grid'
#]]

# output = driver_stats[['Abbreviation', 'win_prob']]
# output = output.sort_values(by='win_prob', ascending=True)

# print('\n Predicted Winner Probabilities for 2025 Canadian Grand Prix: \n')
# print(output.to_string(index=False, float_format='%.3f'))

