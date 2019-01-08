#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 16:51:36 2018

@author: trahman4
"""

import pandas as pd
import datetime
import collections
from datetime import date, timedelta
import csv




dataset_weather = pd.read_csv('KnoxvilleWeather.csv')
df = pd.DataFrame(dataset_weather)

df_weather = df.drop(['dt', 'city_id', 'city_name', 'lat', 'lon', 'sea_level', 'grnd_level',
              'rain_1h', 'rain_3h', 'rain_24h', 'rain_today', 'snow_1h', 'snow_3h',
              'snow_24h', 'snow_today'], axis = 1)

df_weather_numeric = df_weather.drop(['weather_main', 'weather_description', 
                                      'weather_icon'], axis = 1)

df_weather_numeric.sort_values(by='dt_iso', inplace = True)

df_weather_numeric['dt_iso']= df_weather_numeric['dt_iso'].apply(lambda x: 
                    datetime.datetime(int(x.split(" ")[0].split("-")[0]),int(x.split(" ")[0].split("-")[1]),int(x.split(" ")[0].split("-")[2])).date())


image_names_data = pd.read_csv('processed_image_name_data/utid_date.csv')


date_range = []

columns = ['image_name','ut_id','date_from_image/max_date', 'min_date/first date', 'total_in_between_days']
maxdate_mindate = pd.DataFrame(columns = columns)

columns = ['image_name','ut_id/donor','max_date', 'min_date', 'ADD']
donor_max_min_ADD = pd.DataFrame(columns = columns)



columns = ['image_name','max_date', 'min_date', 'ADD']
image_max_min_ADD = pd.DataFrame(columns = columns)

"""columns = ['id','all_weather_dates_for_this_id']
utid_dates_map_string_df  = pd.DataFrame(columns)

columns = ['id','all_weather_dates_for_this_id']
utid_dates_map_df = pd.DataFrame(columns)"""

utid_dates_map = collections.defaultdict(list)
utid_dates_map_string = {}


myString = ''
mr = pd.DataFrame()
 ##finx the appending
#unique_dates = list(set(image_names_data.iloc[:,2].values.tolist()))
        

def find_min_date(image_name,ut_id, max_date):
    global date_range, maxdate_mindate, myString,mr
    date_list = []
    mr = image_names_data.loc[image_names_data['UT_id'].isin([ut_id])]
    
    for row in mr.iterrows():
        curr_date = row[1].values[2]
        
        year, month, day = str(curr_date).split("-")            
        curr_date = date(int(year), int(month), int(day))
            
        year, month, day = str(max_date).split("-")
        max_date = date(int(year), int(month), int(day))
        
        if curr_date <= max_date:
            date_list.append(curr_date)
    
                
    
    value = date_list
    value = sorted(list(set(value)))
    
    myString = ",".join(str(x) for x in value)
    d = {}
    d[max_date] = myString
    utid_dates_map_string[ut_id] = d
    
    
    utid_dates_map[ut_id] = value
    min_date = value[0]
    
    #date_range = pd.date_range(min_date, max_date).tolist()

    date_range = [min_date + timedelta(days=x) for x in range((max_date-min_date).days + 1)]
   
    total_days = len(date_range)
    maxdate_mindate = maxdate_mindate.append({'image_name':image_name,'ut_id':ut_id, 'date_from_image/max_date': max_date, 'min_date/first date': min_date, 'total_in_between_days':total_days},ignore_index=True)
    return min_date
    
    
    
def start():
    i = 0
    global utid_dates_map_string_df, utid_dates_map_df
    for row in image_names_data.iterrows():
        
        image_name = row[1].values[0]
        print("Calculating for image: ", image_name)
        print(i)
        utid = row[1].values[1]
        max_date = row[1].values[2]
        print("max_date: ", max_date)
        min_date = find_min_date(image_name,utid,max_date)
        print("min_date: ", min_date)
        i+=1
        print("Calculating ADD --------------------------------------------\n")
        ADD(image_name, utid,max_date,min_date)
        
    maxdate_mindate.to_csv('outputs/maxdate_mindate.csv', encoding='utf-8', index=False)
    donor_max_min_ADD.to_csv('outputs/donor_max_min_ADD.csv', encoding='utf-8', index=False)
    image_max_min_ADD.to_csv('outputs/image_max_min_ADD.csv', encoding='utf-8', index=False)
    
    
    with open('outputs/utid_dates_map.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['id','all prior weather dates'])
        for key, value in utid_dates_map.items():
           writer.writerow([key, value])
           
    with open('outputs/utid_dates_map_string.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['id','max_date: all prior dates'])
        for key, value in utid_dates_map_string.items():
           writer.writerow([key, value])
    
def  ADD(image_name, utid,max_date,min_date):
    temp_arr = []
    global donor_max_min_ADD,utid_dates_map_df, image_max_min_ADD
    for x in date_range:
        match = df_weather_numeric.loc[df_weather_numeric['dt_iso'].isin([x])]
        total = match['temp'].sum()
        if(match.shape[0] == 0):
            continue
        average_temp = total/match.shape[0]
    
        temp_arr.append(average_temp)
    add = sum(temp_arr)
    
    
    donor_max_min_ADD = donor_max_min_ADD.append({'image_name':image_name, 'ut_id/donor':utid,'max_date':max_date, 'min_date':min_date, 'ADD':add},ignore_index=True)
    image_max_min_ADD = image_max_min_ADD.append({'image_name':image_name,'max_date':max_date, 'min_date':min_date, 'ADD':add},ignore_index=True)

    


#image_names_data = image_names_data[6465:]
start()
