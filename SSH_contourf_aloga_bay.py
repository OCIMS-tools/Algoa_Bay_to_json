#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 15:18:32 2021

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
    date_now=date_ref + timedelta(seconds=np.float64(t)) + timedelta(hours=2) #Add two hours for UTC+2
    date_round = hour_rounder(date_now)
    dates_check.append(date_round)
    dates.append(date_round.timestamp())
    

lon = ds_grid.lon_rho.values
lat = ds_grid.lat_rho.values

ssh = ds.surf_z.values
ssh[np.where(ssh==0)] = np.nan

vmax = np.nanmax(ssh)
vmin = np.nanmin(ssh)

list_geo = []

for x in np.arange(len(ssh)):
    data_crs = ccrs.PlateCarree()

    figure = plt.figure()
    ax = plt.axes(projection=ccrs.epsg(3857))
    contour = ax.contour(lon, lat, ssh[x,:,:],vmin = vmin, vmax = vmax, levels=50, transform=data_crs ,cmap=plt.cm.jet);
    list_geo.append(contour)
    plt.close()


figure = plt.figure()
ax = plt.axes(projection=ccrs.epsg(3857))
contourf = ax.contourf(lon, lat, ssh[x,:,:],vmin = -0.5, vmax = 0.5, levels=50, transform=data_crs ,cmap=plt.cm.jet);


params = {"ytick.color" : "w",
          "xtick.color" : "w",
          "axes.labelcolor" : "w",
          "axes.edgecolor" : "w"}
plt.rcParams.update(params)

#Plotting colorbar
fig,ax = plt.subplots()
cbar = plt.colorbar(contourf,orientation='vertical',extendrect=False)
cbar.set_label('($^\circ$C)')
cd_save_name='SST_colorbar_REMSS.png'
ax.remove()
plt.savefig('colorbar_ssh',transparent=True, format='png',bbox_inches='tight', pad_inches = 0)



features_list = []
counter = 0

for geo_list in list_geo:
    
    # Convert matplotlib contourf to geojson
    contourf_data = geojsoncontour.contour_to_geojson(
        contour=geo_list,
        min_angle_deg=0,
        ndigits=3,
        #stroke_width=0.2,
        #fill_opacity=0.5,
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
    
with open('aloga_ssh_contour.geojson', 'w', encoding='utf-8') as f:
        f.write(str(geojson_data))
        