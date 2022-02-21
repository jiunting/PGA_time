# -*- coding: utf-8 -*-
"""
Created on Sun Feb 20 11:25:12 2022
    
@author: TimLin
"""

from typing import List, TypedDict, Tuple

def build_TauPyModel(home: str, project_name: str,vel_mod_file: str, background_model: str='PREM') -> object:
    #function modified from mudpy
    #https://github.com/dmelgarm/MudPy/blob/master/src/python/mudpy/fakequakes.py
    #vel_mod_file: the full path of .mod file
    #return a .npz file that can be read by TauPyModel
    '''
    This function will take the structure from the .mod file
    and paste it on top of a pre computed mantle structure such as PREM.
    This assumes that the .mod file provided by the user ends with a 0 thickness 
    layer on the MANTLE side of the Moho
    '''
    from numpy import genfromtxt
    from os import environ,path
    from obspy.taup import taup_create, TauPyModel
    import obspy
    import shutil
    #mudpy source folder

    #load user specified .mod infromation
    try:
        structure = genfromtxt(vel_mod_file)
    except:
        structure = genfromtxt(home+'/'+project_name+'/structure/'+vel_mod_file.split('/')[-1])

    if not(path.exists(home+'/'+project_name+'/structure/'+vel_mod_file.split('/')[-1])):
        shutil.copy(vel_mod_file,home+'/'+project_name+'/structure/'+vel_mod_file.split('/')[-1])
    #load background velocity structure
    if background_model=='PREM':
        #get the background file from obspy
        bg_model_file=obspy.__path__[0]+'/taup/data/'+'prem.nd'
        #Q values
        Qkappa=1300
        Qmu=600
        #Write new _nd file one line at a time
        #nd_name=path.basename(vel_mod_file).split('.')[0]
        #nd_name=nd_name+'.nd'
        nd_name=vel_mod_file.split('/')[-1].replace('mod','nd')
        f=open(home+'/'+project_name+'/structure/'+nd_name,'w')
        #initalize
        ztop=0
        for k in range(len(structure)-1):
            #Variables for writing to file
            zbot=ztop+structure[k,0]
            vp=structure[k,2]
            vs=structure[k,1]
            rho=structure[k,3]

            # Write to the file
            line1=('%8.2f\t%8.5f   %7.5f   %7.5f\t%6.1f     %5.1f\n' % (ztop,vp,vs,rho,Qkappa,Qmu))
            line2=('%8.2f\t%8.5f   %7.5f   %7.5f\t%6.1f     %5.1f\n' % (zbot,vp,vs,rho,Qkappa,Qmu))
            f.write(line1)
            f.write(line2)

            #update
            ztop=zbot

        #now read PREM file libe by libne and find appropriate depth tos tart isnerting
        fprem=open(bg_model_file,'r')
        found_depth=False

        while True:

            line=fprem.readline()

            if line=='': #End of file
                break

            if found_depth==False:
                #Check that it's not a keyword line like 'mantle'
                if len(line.split())>1:

                    #not a keyword, waht depth are we at?
                    current_depth=float(line.split()[0])

                    if current_depth > zbot: #PREM depth alrger than .mod file last line
                        found_depth=True
                        f.write('mantle\n')

            #Ok you have found the depth write it to file
            if found_depth == True:
                f.write(line)

        fprem.close()
        f.close()
        # make TauPy npz
        taup_in=home+'/'+project_name+'/structure/'+nd_name
        taup_out=home+'/'+project_name+'/structure/'
        taup_create.build_taup_model(taup_in,output_folder=taup_out)
    else: #To be done later (ha)
        print('ERROR: That background velocity model does not exist')

    return home+'/'+project_name+'/structure/'+nd_name.replace('nd','npz')


def cat2pd(cata_path,description=False):
    '''
        convert USGS catalog format to pandas
    '''
    import pandas as pd
    import os
    #load catalog in pandas
    #read the full path
    if description:
        df = pd.read_csv(cata_path,header=None,skiprows=0,usecols=[0,1,2,3,4,5,10,11,13,14,19],names=['Time','Lat','Lon','Depth','Magnitude','Magtype','Regional','ID','Description','Source_type','review'])
    else:
        df = pd.read_csv(cata_path,header=None,skiprows=0,usecols=[0,1,2,3,4,10,11],names=['Time','Lat','Lon','Depth','Magnitude','Regional','ID'])
        #cat = np.genfromtxt(cata_path, delimiter=',', skip_header=0,usecols=(0,1,2,3,4,10,11), dtype=("|U22",float,float,float,float,"|U2","|U22"))
        #cat = [list(i) for i in cat] #tuple to list
        #df = pd.DataFrame(cat, columns=['Time','Lat','Lon','Depth','Magnitude','Regional','ID'])
    return df


def get_net_sta_loc(home: str, project_name: str, YMD: str='*') -> Tuple[List[str], dict]:
    import glob
    import os
    ###Search through all the event directories and find all the stations (NET.CODE) ###
    EQfolders = home+'/'+project_name+'/waveforms/'+YMD+'*'
    EQfolders = glob.glob(EQfolders)
    same_net_sta_loc = []
    sav_info = {} #dictionary that save the net_station time
    for EQfolder in EQfolders:
        print('In:',EQfolder)
        HNZ_sacs = glob.glob(EQfolder+'/waveforms/*HNZ*.mseed')
        for HNZ_sac in HNZ_sacs:
            HNE_sac = HNZ_sac.replace('HNZ','HNE')
            HNN_sac = HNZ_sac.replace('HNZ','HNN')
            if (not os.path.exists(HNE_sac)) or (not os.path.exists(HNN_sac)):
                continue
            net = HNZ_sac.split('/')[-1].split('.')[0]
            sta = HNZ_sac.split('/')[-1].split('.')[1]
            loc = HNZ_sac.split('/')[-1].split('.')[2]
            #print(net+'_'+sta)
            net_sta_loc = '.'.join([net,sta,loc])
            try:
                sav_info[net_sta_loc].append(EQfolder)
            except:
                sav_info[net_sta_loc] = [EQfolder]
            if not(net_sta_loc in same_net_sta_loc):
                same_net_sta_loc.append(net_sta_loc)

    same_net_sta_loc.sort()
    return same_net_sta_loc, sav_info


def get_staloc(net_sta_key: str, n_date: str) -> List[float]:
    import glob
    from bs4 import BeautifulSoup
    net_sta_loc = net_sta_key.split('.')
    net_sta = '.'.join([net_sta_loc[0],net_sta_loc[1]])
    xml_file = glob.glob(n_date+'/'+'stations/'+net_sta+'.xml')[0]
    tmpIN1 = open(xml_file,'r').read()
    soup = BeautifulSoup(tmpIN1)
    stlon = float(soup.find_all('longitude' or 'Longitude')[0].text)
    stlat = float(soup.find_all('latitude' or 'Latitude')[0].text)
    return stlon,stlat


def get_traveltime(stlon,stlat,eqlon,eqlat,eqdep,model_name='iasp91'):
    from obspy.taup import TauPyModel
    import obspy
    dist_degree=obspy.geodetics.locations2degrees(lat1=eqlat,long1=eqlon,lat2=stlat,long2=stlon)
    model = TauPyModel(model=model_name)
    P=model.get_travel_times(source_depth_in_km=eqdep, distance_in_degree=dist_degree, phase_list=('P','p'), receiver_depth_in_km=0)
    if len(P)==0:
        print('Oops, no P/p ray can be found in given model!')
        for test_model in ['ak135','iasp91','prem']:
            tmp_model = TauPyModel(model=test_model)
            P=tmp_model.get_travel_times(source_depth_in_km=eqdep, distance_in_degree=dist_degree, phase_list=('P','p'), receiver_depth_in_km=0)
            if len(P)!=0:
                print('Use global model for P instead:',test_model)
                break
    S=model.get_travel_times(source_depth_in_km=eqdep, distance_in_degree=dist_degree, phase_list=('S','s'), receiver_depth_in_km=0)
    if len(S)==0:
        print('Oops, no S/s ray can be found in given model!')
        for test_model in ['ak135','iasp91','prem']:
            tmp_model = TauPyModel(model=test_model)
            S=tmp_model.get_travel_times(source_depth_in_km=eqdep, distance_in_degree=dist_degree, phase_list=('S','s'), receiver_depth_in_km=0)
            if len(S)!=0:
                print('Use global model for S instead:',test_model)
                break
    return P[0].time,S[0].time,dist_degree



