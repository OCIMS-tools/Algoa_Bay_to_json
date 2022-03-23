#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:20:58 2021

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


path = '/home/matthew/Documents/Python_scripts/Aloga_model/for_matt/'

fname = 'avg_surf_20210115.nc'
fname_grid = 'grd.nc'

ds = xr.open_dataset(path+fname)

ds_grid = xr.open_dataset(path+fname_grid)

time=ds.time.values

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))


date_ref=datetime(2000,1,1,0,0,0)
#generate a list of dates
dates=[]
dates_check = []
for t in time:
    date_now=date_ref + timedelta(seconds=np.float64(t))
    date_round = hour_rounder(date_now)
    dates_check.append(date_round)
    dates.append(date_round.timestamp())
    

lon = ds_grid.lon_rho.values
lat = ds_grid.lat_rho.values

salt = ds.surf_s.values
salt[np.where(salt==0)] = np.nan

vmax = np.nanmax(salt)
vmin = np.nanmin(salt)

list_geo = []

for x in np.arange(len(salt)):
    data_crs = ccrs.PlateCarree()

    figure = plt.figure()
    ax = plt.axes(projection=ccrs.epsg(3857))
    contourf = ax.contourf(lon, lat, salt[x,:,:],vmin = vmin, vmax = vmax, levels=50, transform=data_crs ,cmap=plt.cm.jet);
    list_geo.append(contourf)
    plt.close()

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

#with open('geojson_contourf_sig_height_5.json', 'w', encoding='utf-8') as f:
#        f.write(geojson_contourf)

    geojson_contourf = ast.literal_eval(contourf_data)

    for x in np.arange(len(geojson_contourf['features'])):
        test = geojson_contourf['features'][x]['properties']
        test.update({"time": dates[counter]})


    t = geojson_contourf['features']
    
    features_list.append(t)
    counter = counter+1
    
    
features = []
for sublist in features_list:
    for item in sublist:
        features.append(item)    
        
geojson_data = FeatureCollection(features)
    
with open('algoa_salt.geojson', 'w', encoding='utf-8') as f:
        f.write(str(geojson_data))
        
