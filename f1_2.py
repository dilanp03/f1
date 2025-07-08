import fastf1 as ff1
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
import numpy as np
import pandas as pd

plotting.setup_mpl(color_scheme='fastf1', misc_mpl_mods=True)
ff1.Cache.enable_cache('cache_dir')
pd.options.mode.chained_assignment = None

race = ff1.get_session(2024, 'Monza', 'R')
race.load()
laps = race.laps
#laps = race._load_laps_data(with_telemetry = True)
# laps_pia = laps.pick_driver('PIA')
# laps_lec = laps.pick_driver('LEC')
laps_selected = laps.pick_drivers(['PIA', 'LEC'])
laps_lec = laps_selected[laps_selected['Driver'] == 'LEC']
laps_pia = laps_selected[laps_selected['Driver'] == 'PIA']
# laps_lec = laps_lec.loc[laps_lec['Stint'] == 2]
# laps_pia = laps_pia.loc[laps_pia['Stint'] == 2]
laps_lec['RaceLapNumber'] = laps_lec['LapNumber'] - 1
laps_pia['RaceLapNumber'] = laps_pia['LapNumber'] - 1
full_distance_lec_pia = pd.DataFrame()
summary_rows = []

for lap_number, lap_data in laps_lec.iterlaps():
    telemetry = lap_data.get_car_data().add_distance().add_driver_ahead()

    # Remove missing DriverAhead data
    telemetry = telemetry.dropna(subset=['DriverAhead'])
    
    # Skip laps with no valid DriverAhead info
    if telemetry.empty:
        #print(f"Lap {lap_number + 1}: no valid DriverAhead data")
        continue

    # Check for Piastri (car number '81') ahead
    if '81' not in telemetry['DriverAhead'].unique():
        #print(f"Lap {lap_number + 1}: Piastri not ahead")
        continue

    telemetry = telemetry.loc[telemetry['DriverAhead'] == '81']

    if telemetry.empty:
        continue

    # Collect telemetry
    lap_telemetry = telemetry[['Distance', 'DistanceToDriverAhead']].copy()
    lap_telemetry['Lap'] = lap_number + 1
    full_distance_lec_pia = pd.concat([full_distance_lec_pia, lap_telemetry])

    summary_rows.append({
        'Lap': lap_number + 1,
        'Mean': np.nanmean(telemetry['DistanceToDriverAhead']),
        'Median': np.nanmedian(telemetry['DistanceToDriverAhead']),
    })


summarized_distance_lec_pia = pd.DataFrame(summary_rows)
plt.rcParams['figure.figsize'] = [10,6]
fig, ax = plt.subplots(2, sharex = True)
fig.suptitle('LEC vs PIA Comparison')

ax[0].plot(laps_lec['RaceLapNumber'], laps_lec['LapTime'], label='LEC')
ax[0].plot(laps_pia['RaceLapNumber'], laps_pia['LapTime'], label='PIA')
ax[0].set(ylabel='Lap Time', xlabel='Lap')
ax[0].legend(loc="upper center")

# Plot distance to driver ahead
ax[1].plot(summarized_distance_lec_pia['Lap'], summarized_distance_lec_pia['Mean'], label='Mean', color='red')
ax[1].plot(summarized_distance_lec_pia['Lap'], summarized_distance_lec_pia['Median'], label='Median', color='grey')
ax[1].set(ylabel='Distance to Driver Ahead (m)', xlabel='Lap')
ax[1].legend(loc="upper center")

# Clean up layout
for a in ax.flat:
    a.label_outer()

plt.tight_layout()
plt.show()

lap_telemetry_lec = laps_lec.loc[laps_lec['RaceLapNumber'] == 20].get_car_data().add_distance()
lap_telemetry_pia = laps_pia.loc[laps_pia['RaceLapNumber'] == 20].get_car_data().add_distance()

distance_lap7 = full_distance_lec_pia.loc[full_distance_lec_pia['Lap']==7]
distance_lap8 = full_distance_lec_pia.loc[full_distance_lec_pia['Lap']==8]
distance_lap9 = full_distance_lec_pia.loc[full_distance_lec_pia['Lap']==9]
distance_lap10 = full_distance_lec_pia.loc[full_distance_lec_pia['Lap']==10]

plt.rcParams['figure.figsize'] = [15,15]
fig, ax = plt.subplots(4)
fig.suptitle('Fastest Lap Telemetry Comparison')

ax[0].title.set_text("Distance to LEC (m)")
ax[0].plot(distance_lap7['Distance'], distance_lap7['DistanceToDriverAhead'], label='Lap 7', linestyle='dotted', color='grey')
ax[0].plot(distance_lap8['Distance'], distance_lap8['DistanceToDriverAhead'], label='Lap 8')
ax[0].plot(distance_lap9['Distance'], distance_lap9['DistanceToDriverAhead'], label='Lap 9', linestyle='dotted', color='white')
ax[0].plot(distance_lap10['Distance'], distance_lap10['DistanceToDriverAhead'], label='Lap 10', linestyle='dashed', color='lightgrey')
ax[0].legend(loc="lower right")
ax[0].set(ylabel='Distance to LEC')

ax[1].title.set_text("Lap 8 telemetry")
ax[1].plot(lap_telemetry_lec['Distance'], lap_telemetry_lec['Speed'], label='LEC')
ax[1].plot(lap_telemetry_pia['Distance'], lap_telemetry_pia['Speed'], label='PIA')
ax[1].set(ylabel='Speed')
ax[1].legend(loc="lower right")

ax[2].plot(lap_telemetry_lec['Distance'], lap_telemetry_lec['Throttle'], label='LEC')
ax[2].plot(lap_telemetry_pia['Distance'], lap_telemetry_pia['Throttle'], label='PIA')
ax[2].set(ylabel='Throttle')

ax[3].plot(lap_telemetry_lec['Distance'], lap_telemetry_lec['Brake'], label='LEC')
ax[3].plot(lap_telemetry_pia['Distance'], lap_telemetry_pia['Brake'], label='PIA')
ax[3].set(ylabel='Brakes')

# ax[4].plot(lap_telemetry_lec['Distance'], lap_telemetry_lec['DRS'], label='LEC')
# ax[4].plot(lap_telemetry_pia['Distance'], lap_telemetry_pia['DRS'], label='PIA')
# ax[4].set(ylabel='DRS')

# Hide x labels and tick labels for top plots and y ticks for right plots.
for a in ax.flat:
    a.label_outer()

plt.show()
