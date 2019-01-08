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

df_weather["date"] = ""

#convert the weather dataset's date to date object date so that we can use the match to find date range
df_weather['date']= df_weather['dt_iso'].apply(lambda x: 
                    datetime.datetime(int(x.split(" ")[0].split("-")[0]),int(x.split(" ")[0].split("-")[1]),int(x.split(" ")[0].split("-")[2])).date())



#this function gets a string in the form of "YYYY-MM-DAY" and return date object    
def make_date(curr_date):
    year, month, day = str(curr_date).split("-")            
    curr_date = date(int(year), int(month), int(day))
    return curr_date    
            

def extract_prior_weather():
    image_name = input("Enter image name: ")
    if " " in image_name:
        image_name = image_name.split()[0]+".JPG"
    match = df_max_min[df_max_min['image_name'].isin([image_name])]
    max_date = match['date_from_image/max_date'].values[0]
    min_date = match['min_date/first date'].values[0]
    min_date = make_date(min_date)
    max_date = make_date(max_date)
    print("Current Date: ",max_date)
    print("Minimum Date: ", min_date)
    date_range = [min_date + timedelta(days=x) for x in range((max_date-min_date).days + 1)]
    in_between_weather = df_weather[df_weather['date'].isin(date_range)]
    return in_between_weather
    
prior_weather = extract_prior_weather()
print(prior_weather)
