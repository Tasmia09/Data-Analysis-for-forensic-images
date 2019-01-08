#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 20:21:31 2018

@author: trahman4
"""
import re
import pandas as pd
from datetime import date, timedelta
import datetime
import operator
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import norm
from collections import defaultdict

dataset_tags = pd.read_csv('scav_mumm.csv').iloc[:,:-1]
dataset_max_min = pd.read_csv('outputs/maxdate_mindate.csv')
dataset_weather = pd.read_csv('KnoxvilleWeather_modified.csv')

scav_df = dataset_tags[dataset_tags['tag'].str.contains('scav')]
mumm_df = dataset_tags[dataset_tags['tag'].str.contains('mumm')]
leg_df = pd.read_csv('leg_data.csv')

columns = ['donor']
donor_max_min_tags = pd.DataFrame(columns=columns)

dataset_weather["date"] = ""

#convert the weather dataset's date to date object date so that we can use the match to find date range
dataset_weather['date']= dataset_weather['dt_iso'].apply(lambda x: 
                    datetime.datetime(int(x.split(" ")[0].split("-")[0]),int(x.split(" ")[0].split("-")[1]),int(x.split(" ")[0].split("-")[2])).date())


donor_match_df = pd.DataFrame
match = pd.DataFrame


weather_description = []
#this function will take a dataframe of certain tags and will return the min date 
#of all the minimum dates of each images and max dates for all maximium...
#meaning each image has a max(current) date and a minimum date...we collect all the minimum dates for all images
#same for max

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
    return processed_date

def collect_max_min_date(i,tag, dataf):
    global donor_match_df,match
    print("We are working on ", tag , " tag")
    dates = []
    donor = choose_donor(i,dataf)
    print("The donor with most data is ", donor)
    donor_match_df = dataf[dataf['image'].str.contains(donor)] #matching the image name with donor's name
    
    for i, row in donor_match_df.iterrows():
        image_name = row.values[0]
        image_name = image_name.split(" ")[0]
        dates.append(return_utid_date(image_name))
    dates = sorted(dates)
    
        
    max_date = max(dates)
    min_date = min(dates)
    print(min_date)
    return donor, max_date, min_date



def choose_donor(i,dataf):
    donors = []
    for row in dataf.iterrows():
        donor_name = row[1].values[0].split(" ")[0].split("_")[0]
        donors.append(donor_name)
    d = defaultdict(int)
    for word in donors:
        d[word] += 1
    d = sorted(d.items(), key=operator.itemgetter(1), reverse = True)
    return d[i][0]

#this function gets a string in the form of "YYYY-MM-DAY" and return date object    
def make_date(curr_date):
    year, month, day = str(curr_date).split("-")            
    curr_date = date(int(year), int(month), int(day))
    return curr_date    
            



def plot_histo(tag,sorted_list,x_label,y_label,title):
    plt.clf()
    x, y = zip(*sorted_list)
    fig, axs = plt.subplots(1,1,figsize=(20,9))
    index = np.arange(len(x))
    plt.barh(index, y, color ='g')
    plt.xlabel(y_label, fontsize=15)
    plt.ylabel(x_label, fontsize=15)
    plt.yticks(index, x, fontsize=15, rotation=30)
    plt.xticks(np.arange(0, 1000, step=50))
    plt.title(title, fontsize=15)
    plt.savefig('images/plt_'+str(tag)+'.png', dpi = 300)
    plt.show()
    

def print_freq_count(sorted_list):  
    print('Weather Type          :  Count')
    for weather_f, count in sorted_list:
        print('{:<20}    : {:>6}'.format(weather_f, count))
        
    ls = [vehicle_body for vehicle_body, count in sorted_list[:]]
        
    print ("Total Number of Weather Types: ", len(ls))
    
    
    
def freq_count(tag, list_to_mr):
    d = defaultdict(int)
    for word in list_to_mr:
        d[word] += 1
    d_sorted = sorted(d.items(), key=operator.itemgetter(1), reverse = True)
    plot_histo(tag, d_sorted, "type", "freq", "histogram for "+str(tag))
    




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
    plt.title(title, fontsize=15)
    plt.show()
    

def calculate_ADD(date_range, tag):
    
    temp_arr = []
    humidity_arr = []
    wind_arr = []
    for x in date_range:
        match = dataset_weather.loc[dataset_weather['date'].isin([x])]
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
    add_values = [temp_add,humidity_add,wind_add]
    if max(add_values) != 0:
        add_values = [float(i)/max(add_values) for i in add_values]

    print(temp_add,humidity_add,wind_add)
    plt.clf()
    x = ['temp_add','humidity_add','wind_add']
    y = add_values
    fig, axs = plt.subplots(1,1,figsize=(20,9))
    index = np.arange(len(x))
    plt.bar(index, y, color ='g')
    plt.xlabel('weather_feature', fontsize=15)
    plt.ylabel("ADD Normalized", fontsize=15)
    plt.xticks(index, x, fontsize=15, rotation=30)
    
    plt.title("ADD for_"+tag, fontsize=15)
    plt.savefig('images/plt_ADD_'+str(tag)+'.png', dpi = 300)
    plt.show()

def start(i,tag, dataf):
    global weather_description,donor_max_min_tags, tag_max_min
    donor, max_date, min_date = collect_max_min_date(i,tag,dataf)
    

    min_date = make_date(min_date)
    max_date = make_date(max_date)
    print("Min Date: ", min_date)
    print("Max Date: ", max_date)
    date_range = [min_date + timedelta(days=x) for x in range((max_date-min_date).days + 1)]
    print(len(date_range))
    
    weather_df = dataset_weather[dataset_weather['date'].isin(date_range)]
    weather_description = weather_df['weather_description'].values.T.tolist()
    if not weather_description or len(date_range) < 10:
        print("NONONO")
        i+=1
        start(i,tag,dataf)
    else:
        freq_count(tag, weather_description)
        calculate_ADD(date_range, tag)


def create_donor_min_max_for_tags(dataf, tag):
    global donor_max_min_tags  
    donors = []
    
    for row in dataf.iterrows():
        donor_name = row[1].values[0].split(" ")[0].split("_")[0]
        donors.append(donor_name)
    donors_list = list(set(donors))
    for donor_name in donors_list:
        dates = []
        donor_match_df = dataf[dataf['image'].str.contains(donor_name)] #matching the image name with donor's name
        
        for i, row in donor_match_df.iterrows():
            image_name = row.values[0]
            image_name = image_name.split(" ")[0]
            dates.append(return_utid_date(image_name))
        dates = sorted(dates)
        
        max_date = max(dates)
        min_date = min(dates)
        donor_max_min_tags = donor_max_min_tags.append({'donor':donor_name,'max_date_'+tag:max_date, 'min_date_'+tag:min_date},ignore_index=True)

        
        """for row in donor_match_df.iterrows():
            image_name = row[1].values[0]
            image_name = image_name.split(" ")[0]      
            match = dataset_max_min[dataset_max_min['image_name'].str.match(image_name)] #matching the image name with tag's data with max_min_date data
            
            max_dates.append(match['date_from_image/max_date'].values[0])
            min_dates.append(match['min_date/first date'].values[0])
        max_date = max(max_dates)
        min_date = min(min_dates)
        donor_max_min_tags = donor_max_min_tags.append({'donor':donor_name,'max_date_'+tag:max_date, 'min_date_'+tag:min_date},ignore_index=True)
"""
        
    
    
      
start(0,"scavenging",scav_df)
start(0,"mummification",mumm_df)
start(0,"leg",leg_df)



#create_donor_min_max_for_tags(leg_df, "leg")
#donor_max_min_tags.to_csv('outputs/donor_max_min_'+"leg"+'.csv', encoding='utf-8', index=False)

#create_donor_min_max_for_tags(mumm_df, "mummification")
#donor_max_min_tags.to_csv('outputs/donor_max_min_'+"mumm"+'.csv', encoding='utf-8', index=False)

#plot_normal_distribution(scav_weather_df['humidity'],'scav weather humidity')

