#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crime.time()eated on Fri Jan 15 11:00:36 2021

@author: matthew
"""

import matplotlib.pyplot as plt
import xarray as xr
import geojsoncontour
import numpy as np
import ast
from geojson import FeatureCollection
import cartopy.crs as ccrs
from datetime import timedelta, date, datetime


#Setting path and filenames to import
path = '/home/matthew/Documents/Python_scripts/Aloga_model/for_matt/'
fname = 'avg_surf_20210115.nc'
fname_grid = 'grd.nc'

#Setting path and and filename to save geojson file 
save_fname = 'algoa_ocims_test.topojson'
save_path = '/home/matthew/Documents/Python_scripts/Aloga_model/'

#Opening dataset with xarray for surface file and grid file 
ds = xr.open_dataset(path+fname)
ds_grid = xr.open_dataset(path+fname_grid)

#Loading variables from file 

#Loading time 
time=ds.time.values

#Rounding off model time to close hour (seconds slighty different)

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

#Time of intialiasion hard coded from file 
date_ref=datetime(2000,1,1,0,0,0)

#generate a list of dates
dates=[]
dates_check = []
for t in time:
    date_now=date_ref + timedelta(seconds=np.float64(t))
    date_round = hour_rounder(date_now)
    dates_check.append(date_round)
    dates.append(date_round.timestamp())
    
#Load lon and lat grid 
lon = ds_grid.lon_rho.values
lat = ds_grid.lat_rho.values

#Loading sst from file 
sst = ds.surf_t.values
sst[np.where(sst==0)] = np.nan

#Creating a list of contourf plots to be converted to geojson 
list_geo = []

for x in np.arange(len(sst)):
    data_crs = ccrs.PlateCarree()

    figure = plt.figure()
    ax = plt.axes(projection=ccrs.epsg(3857))
    contourf = ax.contourf(lon, lat, sst[x,:,:],vmin = 15, vmax = 26, levels=50, transform=data_crs ,cmap=plt.cm.jet);
    list_geo.append(contourf)
    plt.close()
    
figure = plt.figure()
ax = plt.axes(projection=ccrs.epsg(3857))
contourf = ax.contourf(lon, lat, sst[x,:,:],vmin = 15, vmax = 26, levels=50, transform=data_crs ,cmap=plt.cm.jet);


figure = plt.figure()
plt.colorbar(contourf)


params = {"ytick.color" : "w",
          "xtick.color" : "w",
          "axes.labelcolor" : "w",
          "axes.edgecolor" : "w"}
plt.rcParams.update(params)

#Plotting colorbar
fig,ax = plt.subplots()
plt.colorbar(contourf,orientation='vertical',extendrect=False)
cd_save_name='SST_colorbar_REMSS.png'
ax.remove()
plt.savefig('colorbar',transparent=True, format='png',bbox_inches='tight', pad_inches = 0)




#Creating a list of geojson ready files from the contourf plots using "geojsoncontour.contourf_to_geojson"
features_list = []
counter = 0

for geo_list in list_geo:
    
    # Convert matplotlib contourf to geojson
    contourf_data = geojsoncontour.contourf_to_geojson(
        contourf=geo_list,
        min_angle_deg=0,
        ndigits=3,
        stroke_width=0.2,
        fill_opacity=0.5,
        unit='c'

    )

    #Changing the format to be able to edit properties in geojson file 
    geojson_contourf = ast.literal_eval(contourf_data)

    #Adding time dimesion to geojson properties 
    for x in np.arange(len(geojson_contourf['features'])):
        test = geojson_contourf['features'][x]['properties']
        test.update({"time": dates[counter]})


    t = geojson_contourf['features']
    
    features_list.append(t)
    counter = counter+1
    
#Combine the list of geojson formatted variable     
features = []
for sublist in features_list:
    for item in sublist:
        features.append(item)    
        
#Adding a featrecollection to the combined list (geojson formatted variable)        
geojson_data = FeatureCollection(features)

#Save geojson using save_path and save_fname     
with open(save_path+save_fname, 'w', encoding='utf-8') as f:
        f.write(str(geojson_data))
        

