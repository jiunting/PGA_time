# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 21:42:12 2022
    
@author: TimLin
"""

import glob
import obspy
from obspy import UTCDateTime
import numpy as np
import src.analysis as analysis
import pandas as pd
import matplotlib.pyplot as plt

home = "/hdd/jtlin"
project_name = "SMData_CA"

catalog = "/hdd/jtlin/SMData_CA/catalog/CA.cat"
cat = analysis.cat2pd(catalog)

T = pd.to_datetime(cat['Time'],format='%Y-%m-%dT%H:%M:%S.%fZ')

# velmod
vel_mod = "/hdd/jtlin/SMData_CA/structure/Vel1D_CA.mod"
vel_mod_path = analysis.build_TauPyModel(home, project_name,vel_mod) 

# get eq_dirs
eq_dirs = glob.glob(home+"/"+project_name+"/waveforms/*")

# sampling
sampl = 100

nev = 0
for eq_dir in eq_dirs:
    if nev%10==0:
        print('current n=',nev)
    eq_time = eq_dir.split("/")[-1]
    eq_time_obj = UTCDateTime(eq_time)
    # get EQinfo by EQ time
    idx = T[np.abs(T-eq_time_obj.datetime)==min(np.abs(T-eq_time_obj.datetime))]
    if len(idx)!=1:
        print('=======catalog ambiguous....skip this date============')
        print(eq_time)
        print(cat.iloc[idx])
        continue # datetime and catalog is ambiguous
    idx = idx.index[0]
    evlo = cat.iloc[idx].Lon
    evla = cat.iloc[idx].Lat
    evdep = cat.iloc[idx].Depth
    # start dealing with stations
    net_sta_locs, d_path = analysis.get_net_sta_loc(home, project_name, eq_time)
    for net_sta_loc in net_sta_locs:
        Z_file = glob.glob(home+"/"+project_name+"/waveforms/"+eq_time+"/waveforms/"+net_sta_loc+".HNZ*mseed")
        E_file = glob.glob(home+"/"+project_name+"/waveforms/"+eq_time+"/waveforms/"+net_sta_loc+".HNE*mseed")
        N_file = glob.glob(home+"/"+project_name+"/waveforms/"+eq_time+"/waveforms/"+net_sta_loc+".HNN*mseed")
        assert len(Z_file)==len(E_file)==len(N_file)==1, "E/N/Z multiple files"
        Z = obspy.read(Z_file[0])
        E = obspy.read(E_file[0])
        N = obspy.read(N_file[0])
        # process data and make sure they are all in the same length
        E.detrend('linear')
        N.detrend('linear')
        Z.detrend('linear')
        E.trim(starttime=eq_time_obj-1, endtime=eq_time_obj+301,pad=True,fill_value=0)
        N.trim(starttime=eq_time_obj-1, endtime=eq_time_obj+301,pad=True,fill_value=0)
        Z.trim(starttime=eq_time_obj-1, endtime=eq_time_obj+301,pad=True,fill_value=0)
        E.interpolate(sampling_rate=sampl, starttime=eq_time_obj,method='linear')
        N.interpolate(sampling_rate=sampl, starttime=eq_time_obj,method='linear')
        Z.interpolate(sampling_rate=sampl, starttime=eq_time_obj,method='linear')
        E.trim(starttime=eq_time_obj, endtime=eq_time_obj+300,pad=True,fill_value=0)
        N.trim(starttime=eq_time_obj, endtime=eq_time_obj+300,pad=True,fill_value=0)
        Z.trim(starttime=eq_time_obj, endtime=eq_time_obj+300,pad=True,fill_value=0)
        # PGA
        max_idx = np.argmax(Z[0].data**2+E[0].data**2+N[0].data**2)
        PGA_time = E[0].times()[max_idx]
        # get staloc
        stlo,stla = analysis.get_staloc(net_sta_loc, d_path[net_sta_loc][0])
        dist = obspy.geodetics.locations2degrees(lat1=evla,long1=evlo,lat2=stla,long2=stlo)
        # get P/S arrival time
        P,S,dist = analysis.get_traveltime(stlo,stla,evlo,evla,evdep,model_name=vel_mod_path)
        #print(P,S,dist)
        # make some plot
        plt.plot(dist,P,'k.',markersize=1)
        plt.plot(dist,S,'r.',markersize=1)
        plt.plot(dist,PGA_time,'m*',markersize=1)
    nev += 1
    if nev==100:
        break

plt.xlabel('Dist (deg)',fontsize=14)
plt.ylabel('Time (s)',fontsize=14)
#plt.savefig('time_pga.png')


