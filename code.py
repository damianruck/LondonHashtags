import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('data/hashtagCountsPerDayLondon.csv')#,nrows=200000)
df['date'] = pd.to_datetime(df['date'])

print('# hashtag-days:',len(df.index))
print('date range:',df['date'].min(),df['date'].max())

s=df.groupby(['hashtag'],as_index=False).agg({'count':'sum'}).sort_values('count',ascending=False)
s.index=range(1,len(s.index)+1)
