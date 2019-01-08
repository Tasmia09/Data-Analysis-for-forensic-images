#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 14:37:11 2018

@author: trahman4
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd

import re



def plot_normal_distribution(temp, column_name):
    
    mu, std = norm.fit(temp)
    
    plt.hist(temp, bins=25, density=True, alpha=0.6, color='g')
    
    # Plot the PDF.
    xmin, xmax = plt.xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k', linewidth=2)
    title = "Normal Distribution of %s\nFit results: mu = %.2f,  std = %.2f" % (column_name,
                                                                                mu, std)
    plt.title(title)
    plt.show()


#importing the dataset
dataset_weather = pd.read_csv('KnoxvilleWeather.csv')
dataset_dates = pd.read_csv('all_image_paths_10242018_forTasmia.csv')

dataset_dates.columns = ['Date(MM-DD-YY)']

df = pd.DataFrame(dataset_weather)
df_weather = df.drop(['dt', 'city_id', 'city_name', 'lat', 'lon', 'sea_level', 'grnd_level',
              'rain_1h', 'rain_3h', 'rain_24h', 'rain_today', 'snow_1h', 'snow_3h',
              'snow_24h', 'snow_today'], axis = 1)

df_weather_numeric = df_weather.drop(['dt_iso','weather_main', 'weather_description', 
                                      'weather_icon'], axis = 1)
#dataset_dates = dataset_dates.iloc[454988:455011,:]

index_faults = []

format_val_5_index = []
format_val_6_index = []
format_val_7_index = []

ut_id_list = []
date_list = []

#creating a panda where we will save the donors and dates of each image
columns = ['Image_name','UT_id', 'date_only(YYYY-MM-DD)']
new_dataset_dates = pd.DataFrame(columns = columns)

#this formatting is adapted for the dataset I observed
def image_names_formatting():
    
    q = re.compile('\d+')
    i = 0
    for row in dataset_dates.iterrows():
        
        date = row[1].values
        formats = q.findall(date[0])
        if len(formats)  < 5:
           
            index_faults.append(i)
            
        elif len(formats)  == 5:
            
            format_val_5_index.append(i)
        elif len(formats)  == 6:
            format_val_6_index.append(i)
        elif len(formats)  == 7:
            format_val_7_index.append(i)
        
        i+=1
    #dataset_dates = dataset_dates.drop(dataset_dates.index[index_faults[0]:index_faults[len(index_faults)-1]])
    
    
    indexes_to_keep = set(range(dataset_dates.shape[0])) - set(index_faults)
    dataset_dates_no_error = dataset_dates.take(list(indexes_to_keep))
    
    indexes_to_keep = set(range(dataset_dates.shape[0])) - set(index_faults+format_val_6_index+ format_val_7_index)
    dataset_dates_format_5 = dataset_dates.take(list(indexes_to_keep))
    
    indexes_to_keep = set(range(dataset_dates.shape[0])) - set(index_faults+format_val_5_index+ format_val_7_index)
    dataset_dates_format_6 = dataset_dates.take(list(indexes_to_keep))
    
    indexes_to_keep = set(range(dataset_dates.shape[0])) - set(index_faults+format_val_5_index+ format_val_6_index)
    dataset_dates_format_7 = dataset_dates.take(list(indexes_to_keep))
    
    
    dataset_dates_no_error.to_csv('processed_image_name_data/dataset_dates_no_error.csv', encoding='utf-8', index=False)
    dataset_dates_format_5.to_csv('processed_image_name_data/dataset_dates_format_5.csv', encoding='utf-8', index=False)
    dataset_dates_format_6.to_csv('processed_image_name_data/dataset_dates_format_6.csv', encoding='utf-8', index=False)
    dataset_dates_format_7.to_csv('processed_image_name_data/dataset_dates_format_7.csv', encoding='utf-8', index=False)


pre_year=0


#this function will take a image name and will return the donor and specific date format to match with weather data's dates
def return_utid_date(name):
    global pre_year
    q = re.compile('\d+')
    ut_id, date = name.upper().split('_',1)
    if "D" not in ut_id:
            ut_id = ut_id+" "
    formats = q.findall(date)
    month, day, year = formats[0], formats[1], formats[2]
    
    #these modifications are specific to the data
    if (year == "2"):
        year = str(pre_year)
    elif(year == "0216"):
        year = pre_year
        
    elif(len(year)==2):
        year = "20"+year
    elif(len(year)==3):
        year = pre_year
    if (len(day) == 3):
        day = day[0]+day[1]
        
    processed_date = year + '-' + month + '-' + day
    #processed_date = datetime.datetime(int(year), int(month), int(day)).date()
    pre_year = year
    return ut_id, processed_date


def create_csv_utid_date():
    global new_dataset_dates, ut_id_list, date_list
    i = 0
    #image_name = input("Enter image name: ")
    for row in dataset_dates_format6.iterrows():
        image_name = str(row[1].values[0])
        
        utid, max_date = return_utid_date(image_name)
        ut_id_list.append(utid)
        date_list.append(max_date)
        
        
        new_dataset_dates = new_dataset_dates.append({'Image_name':image_name,'UT_id': utid, 'date_only(YYYY-MM-DD)': max_date},ignore_index=True)
        i+=1
    new_dataset_dates.to_csv('processed_image_name_data/utid_date.csv', encoding='utf-8', index=False)
    
    ut_id_list = sorted(list(set(ut_id_list)))
    date_list = sorted(list(set(date_list)))
    
    ut_id_list = pd.DataFrame({'unique_ut_id_list':ut_id_list})
    date_list = pd.DataFrame({'unique_date_list(YY-MM-DD)':date_list})
  
    ut_id_list.to_csv('processed_image_name_data/unique_ut_id_list.csv', encoding='utf-8', index=False)
    date_list.to_csv('processed_image_name_data/unique_date_list.csv', encoding='utf-8', index=False)


    

#image_names_formatting()

dataset_dates_format6 = pd.read_csv('processed_image_name_data/unique_image_names.csv')
#dummy_dataset_dates = dataset_dates_format6[:5]
create_csv_utid_date()







