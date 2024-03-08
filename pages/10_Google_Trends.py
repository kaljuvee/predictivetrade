from pytrends.request import TrendReq
import matplotlib.pyplot as plt

pytrends = TrendReq(hl='en-US', tz=360)

data  = pytrends.get_historical_interest(["Airbnb share price", 'Airbnb price'], year_start=2020, month_start=12, day_start=10, hour_start=0, year_end=2020,
                                 month_end=12, day_end=11, hour_end=0, cat=0, geo='', gprop='', sleep=0)

data

plt.figure(figsize=(20, 10))
plt.plot(data["SLACK share price"])
plt.plot(data["SLACK price"])
plt.legend(['Pynk.io', 'Google'])

data.sort_values("TRIP stock price")

data.index = data.index.strftime('%2020/%m/%d')
data.groupby('date').mean()


