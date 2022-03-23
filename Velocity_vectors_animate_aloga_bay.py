#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  1 11:33:27 2021

@author: matthew
"""
import json
import xarray as xr
import numpy as np
import datetime
from geopy import Point                                                                                                                                                                       
from geopy.distance import geodesic                                                                                                                                                           
from metpy import calc                  
from metpy.units import units
from geojson import FeatureCollection
import numpy as np
from netCDF4 import Dataset
import croco_tools_visualisation as croco
from datetime import timedelta, date, datetime
from global_land_mask import globe

from scipy.interpolate import griddata
# %%

def find_coordinate(lon,lat,u,v,scale):
    #Calulating resulant speed which is used for length 
    dist = np.sqrt(u * u + v * v)
    dist = dist+scale
    
    #Calulating direction as a bearing 
    u1 = units.Quantity(u, "m/s")                                                                                                                                                      
    v1 = units.Quantity(v, "m/s")     
    dirc_temp = calc.wind_direction(u1,v1,convention='to')
    
    dirc_convert = str(dirc_temp)
    dirc = float(dirc_convert[0:3])       
                                                                                                                                                                            
    point2 = (geodesic(kilometers=dist).destination(Point(lat, lon), dirc).format_decimal())   
    point_list = point2.split(",")       
    lat2 = float(point_list[1])  
    lon2 = float(point_list[0])   
                                                                                   
    
    return lat2, lon2, dirc

def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

# %%

path = '/home/matthew/Documents/Python_scripts/Aloga_model/for_matt/'

fname = 'avg_surf_20210115.nc'
fname_grid = 'grd.nc'


ds = xr.open_dataset(path+fname)

ds_grid = xr.open_dataset(path+fname_grid)

# get the time
nc_id_avg = Dataset(fname, 'r')
time = nc_id_avg.variables['time'][:]
# time origin (needs to be hard coded here as it is not written to the croco output file)
date_ref=datetime(2000,1,1,0,0,0)
#generate a list of dates
dates=[]
date_str=[]
for t in time:
    date_now=date_ref + timedelta(seconds=np.float64(t))
    #dates.append(date_now)
    date_round = hour_rounder(date_now)
    date_str.append(date_round)
    dates.append(date_round.timestamp())

dates[0:240:3]

step = 4
latp,lonp,u,v=croco.get_uv_surf(fname,fname_grid,0,step)
        

lat_test = np.meshgrid([np.arange(start=np.nanmin(latp), stop=np.nanmax(latp), step=0.05)])
lon_test = np.meshgrid([np.arange(start=np.nanmin(lonp), stop=np.nanmax(lonp), step=0.05)])

grid = np.meshgrid(lon_test,lat_test)

#Mask
#grid_lat[]
#grid_lat = np.zeros(np.shape(latp))
#for x in np.arange(len(latp[0,:])):
#         lat_tmp = np.arange(start=np.round(np.nanmin(latp[0,x]),3), stop=np.round(np.nanmin(latp[0,x]),3)+(26.5*0.05), step=0.05)
#         grid_lat[:,x] = lat_tmp[:]
             
#grid_lat[]
#grid_lon = np.zeros(np.shape(lonp))
#for x in np.arange(len(lonp[:,0])):
#         lon_tmp = np.arange(start=np.round(np.nanmin(lonp[0,x]),3), stop=np.round(np.nanmin(lonp[0,x]),3)+(38*0.01), step=0.01)
#         grid_lon[x,:] = lon_tmp[:]
             
#grid_u = griddata((lonp_array,latp_array), u_array,  (grid_lon, grid_lat), method='nearest')

pad = np.zeros(np.shape(u)[1])

lonp_array = np.array(lonp).flatten()
latp_array = np.array(latp).flatten()
u_array = np.array(u).flatten()

is_on_land = globe.is_land(grid[1],grid[0])

counter = 0

for x in np.arange(len(dates)):
    save_step = counter
    #get lon and lat
    step=4 # for thinning out the u,v vectors
    latp,lonp,u,v=croco.get_uv_surf(fname,fname_grid,save_step,step)

    u[0,:]=np.nan
    v[0,:]=np.nan

    u_array = np.array(u).flatten()
    v_array = np.array(v).flatten()

    grid_u = griddata((lonp_array,latp_array), u_array,  (grid[0], grid[1]), method='nearest')
    grid_v = griddata((lonp_array,latp_array), v_array,  (grid[0], grid[1]), method='nearest')

    grid_u[is_on_land==True]=np.nan
    grid_v[is_on_land==True]=np.nan

    grid_u[np.where(np.isnan(grid_u))] = 0
    grid_v[np.where(np.isnan(grid_v))] = 0
   
    dx =  np.round(lat_test[0][1]-lat_test[0][0],3)
    dy =  np.round(lon_test[0][1]-lon_test[0][0],3)
    la1 = np.round(np.max(grid[1]),3)
    la2 = np.round(np.min(grid[1]),3)
    lo1 = np.round(np.min(grid[0]),3)
    lo2 = np.round(np.max(grid[0]),3) 
    ny = np.shape(grid[0])[0]
    nx = np.shape(grid[0])[1]
    reftime = date_str[1]

    data_v = {}

    header={
        
        'dx': float(dx),
        'dy': float(dy),
        'la1': float(la1),
        'la2': float(la2),
        'lo1': float(lo1),
        'lo2': float(lo2),
        'nx': nx,
        'ny': ny,
        'parameterCategory': 2,
        'parameterNumber': 3,
        'parameterNumberName': 'Northward current', 
        'parameterUnit': 'm.s-1',
       
   
    }
    data_v['header'] = header

    #Reshaping data
    data_tmp = grid_v[::-1]
    data_tmp = np.reshape(data_tmp, -1)
    data_list=[]

    #loop to put the data in list 
    count = np.arange(len(data_tmp))
    for i in count:
        data_list.append(float(data_tmp[i]))

    #data_list.reverse()
    data_v['data'] = data_list

    data_u = {}
    header={
    
        'dx': float(dx),
        'dy': float(dy),
        'la1': float(la1),
        'la2': float(la2),
        'lo1': float(lo1),
        'lo2': float(lo2),
        'nx': nx,
        'ny': ny,
        'parameterCategory': 2,
        'parameterNumber': 2,
        'parameterNumberName': 'Eastward current', 
        'parameterUnit': 'm.s-1',
        'time': 1451424600,

    }
    data_u['header'] = header

    #Reshaping data 
    data_tmp = grid_u[::-1]
    data_tmp = np.reshape(data_tmp, -1)
    data_list=[]

    #loop to put the data in list 
    count = np.arange(len(data_tmp))
    for i in count:
        data_list.append(float(data_tmp[i]))

    #data_list.reverse()
    #Adding to dict    
    data_u['data'] = data_list
    
    data_final = [data_u,data_v]

    with open('current_'+str(save_step)+'h''.json', 'w', encoding='utf-8') as f:
        json.dump(data_final, f, ensure_ascii=False, indent=4)
        
    counter = counter+1


