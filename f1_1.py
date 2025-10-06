import fastf1
import os

os.makedirs('cache_dir', exist_ok=True)
fastf1.Cache.enable_cache('cache_dir')

schedule = fastf1.get_event_schedule(2025)
print(schedule)
print(schedule.columns)
print(schedule.loc[:,['RoundNumber', 'Country', 'Location', 'EventFormat', 'Session5', 'Session5DateUtc']])

# session = fastf1.get_session(2025,7,'R')
# session.load()
# results = session.results.loc[:,['Abbreviation', 'TeamName', 'ClassifiedPosition', 'Points']]
# print(results)

# fastest = session.laps.pick_fastest()
# print(fastest)
