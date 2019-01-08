#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 24 13:17:00 2018

@author: trahman4
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 20:21:31 2018

@author: trahman4
"""


import pandas as pd
from datetime import date, timedelta
import datetime



df_max_min = pd.read_csv('outputs/maxdate_mindate.csv')
df_weather = pd.read_csv('KnoxvilleWeather_modified.csv')

columns = ['image_name','max_date', 'min_date', 'ADD_temp', 'ADD_humidity', 'ADD_wind_speed']
image_max_min_ADD = pd.DataFrame(columns = columns)

df_weather["date"] = ""

#convert the weather dataset's date to date object date so that we can use the match to find date range
df_weather['date']= df_weather['dt_iso'].apply(lambda x: 
                    datetime.datetime(int(x.split(" ")[0].split("-")[0]),int(x.split(" ")[0].split("-")[1]),int(x.split(" ")[0].split("-")[2])).date())



#this function gets a string in the form of "YYYY-MM-DAY" and return date object    
def make_date(curr_date):
    year, month, day = str(curr_date).split("-")            
    curr_date = date(int(year), int(month), int(day))
    return curr_date    
            

def extract_prior_weather(image_name):
    
    match = df_max_min[df_max_min['image_name'].isin([image_name])]
    max_date = match['date_from_image/max_date'].values[0]
    min_date = match['min_date/first date'].values[0]
    min_date = make_date(min_date)
    max_date = make_date(max_date)
    print("Current Date: ",max_date)
    print("Minimum Date: ", min_date)
    date_range = [min_date + timedelta(days=x) for x in range((max_date-min_date).days + 1)]
    #in_between_weather = df_weather[df_weather['date'].isin(date_range)]
    return max_date, min_date, date_range
    
def start():
    global image_max_min_ADD
    
    for i,row in df_max_min.iterrows():
        print(i)
        image_name = row['image_name']
        max_date, min_date, date_range = extract_prior_weather(image_name)
        temp_arr = []
        humidity_arr = []
        wind_arr = []
        for x in date_range:
            match = df_weather.loc[df_weather['date'].isin([x])]
            temp_total = match['temp'].sum()
            humidity_total = match['humidity'].sum()
            wind_total = match['wind_speed'].sum()
            if(match.shape[0] == 0):
                continue
            average_temp = temp_total/match.shape[0]
            average_humidity = humidity_total/match.shape[0]
            average_wind = wind_total/match.shape[0]
        
            temp_arr.append(average_temp)
            humidity_arr.append(average_humidity)
            wind_arr.append(average_wind)
        temp_add = sum(temp_arr)
        humidity_add = sum(humidity_arr)
        wind_add = sum(wind_arr)
        image_max_min_ADD = image_max_min_ADD.append({'image_name':image_name,'max_date':max_date, 'min_date':min_date, 'ADD_temp':temp_add,'ADD_humidity':humidity_add, 'ADD_wind_speed':wind_add},ignore_index=True)


start()
image_max_min_ADD.to_csv('outputs/image_max_min_all_ADD.csv', encoding='utf-8', index=False)




