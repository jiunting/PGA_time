import src.analysis as analysis
import numpy as np

home = "/hdd/jtlin"
project_name = "SMData_CA"

same_net_sta_loc, sav_info = analysis.get_net_sta_loc(home, project_name)
#sav_stlo = []
#sav_stla = []
fout = open('CA_station.txt','w')
for st in same_net_sta_loc:
    stlo, stla = analysis.get_staloc(st,sav_info[st][0])
    fout.write('%s %f %f\n'%(st,stlo,stla))
    #sav_stlo.append(stlo)
    #sav_stla.append(stla)

fout.close()
#print(sav_stlo,sav_stla)
