import matplotlib.pyplot as plt
import fastf1 as f1
from fastf1 import plotting

f1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False, color_scheme='fastf1')

session = f1.get_session(2025, 4, 'R')
session.load(telemetry=False, weather=False)
fig, ax = plt.subplots(figsize=(8, 5))

for drv in session.drivers:
    drv_laps = session.laps.pick_drivers(drv)
    abb = drv_laps['Driver'].iloc[0]
    style = f1.plotting.get_driver_style(identifier=abb,
                                         style=['color', 'linestyle'],
                                         session=session)
    ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)

ax.set_ylim([20.5, 0.5])
ax.set_yticks([1, 5, 10, 15, 20])
ax.set_xlabel('Lap')
ax.set_ylabel('Position')
ax.legend(bbox_to_anchor=(1.0, 1.02))
plt.tight_layout()
plt.show()

