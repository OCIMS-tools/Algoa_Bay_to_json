#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 16:11:50 2021

@author: matthew
"""

import numpy as np
import xarray as xr 
import pylab  as plt
import cartopy.crs as ccrs
import cartopy
from geojson import FeatureCollection
from datetime import timedelta, date, datetime


# %% Loading dataset

ds = xr.open_dataset('parcels_output_20210225.nc',decode_times=False)

# %% Loading variables needed 

#Loading trajectories
traj = ds.trajectory.values
# Loading time 
time = ds.time.values
# Loading lon and lat
lon = ds.lon.values
lat = ds.lat.values

#lat = lat[0:20,:]
#lon = lon[0:20,:]
#time = time[0:20,:]

lat_array = np.squeeze(lat.flatten())
lon_array = np.squeeze(lon.flatten())
time_array = np.squeeze(time.flatten())

lon_array = lon_array[~np.isnan(time_array)]
lat_array = lat_array[~np.isnan(time_array)]
time_array = time_array[~np.isnan(time_array)]

#lon_array[np.isnan(lon_array)]= 0;
#lat_array[np.isnan(lat_array)]= 0;
#time_array[np.isnan(time_array)]= -10;




# %% Converting time stamp

#Finding time since intialation ds.time.units
time_ref_year = int(ds.time.units[14:18])
time_ref_month = int(ds.time.units[19:21])
time_ref_day = int(ds.time.units[22:24])
time_ref_hour = int(ds.time.units[25:27])
time_ref_minute = int(ds.time.units[28:30])

#Reference time for seconds since intialation 
date_ref=datetime(time_ref_year,time_ref_month,time_ref_day,time_ref_hour,time_ref_minute,0)



def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

#generate a list of dates
dates=[]
dates_check = []
for t in time_array:
    date_now=date_ref + timedelta(seconds=np.float64(t))
    date_round = hour_rounder(date_now)
    dates_check.append(date_round)
    dates.append(date_round.timestamp())
    

# %% Looping through values to create diction in geojson format

x = {}
for i in np.arange(len(time_array)):
    x[i]={
         "type": "Feature",
         "geometry": {
             "type": "Point",
             "coordinates":[ 
                    lon_array[i],
                    lat_array[i]
                    ]   
             },
             "properties": {
                "time":dates[i],"name": "spill particle","latitude":lat_array[i],"longitde":lon_array[i]
                }
            }   
        
xy = []
for ip in np.arange(len(time_array)):
            xy.append(x[ip])
            
geojson_data = FeatureCollection(xy)

 
# %% Saving geojson file
 
with open('spill_test_final_nan.geojson', 'w', encoding='utf-8') as f:
        f.write(str(geojson_data))
         
    


