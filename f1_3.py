from matplotlib import pyplot as plt
import fastf1 as f1
from fastf1 import plotting

f1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=False, color_scheme='fastf1')

race = f1.get_session(2025, 'Japan', 'R')
race.load()

fig,ax = plt.subplots(figsize=(8,5))

for driver in ('VER', 'LEC', 'PIA', 'HAM'):
    laps = race.laps.pick_drivers(driver).pick_quicklaps().reset_index()
    style = plotting.get_driver_style(identifier=driver,
                                      style=['color', 'linestyle'],
                                      session=race)
    ax.plot(laps['LapTime'], **style, label=driver)

ax.set_xlabel('Lap Number')
ax.set_ylabel('Lap Time')
ax.legend()
plotting.add_sorted_driver_legend(ax, race)
plt.show()

