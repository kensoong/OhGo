import re
import urllib2
import MySQLdb
import json
import numpy as np
from mapquest_utils import *
import math
import mysqlconnect as msc


def distance_on_unit_sphere(lat1, long1, lat2, long2):

    degrees_to_radians = math.pi/180.0

    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    return arc*6378137.0 # return in meters

def make_dist_vec(s1,e1,M=-1):
    # makes the distance vector given start and end point
    
    # passing in lat,lng coordinates
    s1latlng = s1.split(',')
    s1latlng = [float(s1latlng[0]),float(s1latlng[1])] 
    e1latlng = e1.split(',')
    e1latlng = [float(e1latlng[0]),float(e1latlng[1])]
    
    #print e1latlng
        
    if M==-1:
        conn = msc.mysqlcon()
        x = conn.cursor()
        
        
    x.execute('select nid, lat, lng from foursquare join foursquare_id on foursquare.id=foursquare_id.id order by nid');
    result = x.fetchall()
    
            
    lat_s = s1latlng[0]
    lng_s = s1latlng[1]
    
    lat_e = e1latlng[0]
    lng_e = e1latlng[1]
    
    dist_s = [distance_on_unit_sphere(lat_s,lng_s,lat_e,lng_e)]
    dist_e = [dist_s[0]]

    for c1 in range(len(result)):
        
        lat1 = result[c1][1]
        lng1 = result[c1][2]

        dr_s = distance_on_unit_sphere(lat1, lng1, lat_s, lng_s)
        dr_e = distance_on_unit_sphere(lat1, lng1, lat_e, lng_e)
        
        dist_s.append(dr_s)
        dist_e.append(dr_e)

    if M==-1:
        conn.close()
        x.close()
        
    return dist_s, dist_e

def top5dist(mcn,dist,rrest,start1='Palo Alto, CA',end1='Stanford, CA',M=-1,nc=5):
        
    sugg = mcn[0]-mcn[0]  
    for r in rrest:
        sugg += mcn[r]
    
    for r in rrest:
        sugg[r]=0
    
    # make NxM matrix of relevant distances
    dmat = []
    for rr in rrest:
        dmat.append(np.append(0,dist[rr-1]))
    
    # append start and end locations
    dist_start, dist_end = make_dist_vec(start1,end1)
    dmat.append(dist_start)
    dmat.append(dist_end)
        
    dmat = np.array(dmat)
    
    # find closest points
    dx = [0]
    for ig in range(len(mcn)):
        if ig:
            closest = dmat[:,ig]
            cig = closest.argsort()[:2]
            x1 = closest[cig[0]]+closest[cig[1]]
            
            # insert if cases here
            if (len(rrest) in cig) and ((len(rrest)+1) in cig):
                x2 = dmat[len(rrest)][0]
            elif (len(rrest) in cig):
                x2 = dmat[len(rrest)][rrest[min(cig)]]
            elif ((len(rrest)+1) in cig): 
                x2 = dmat[len(rrest)+1][rrest[min(cig)]] 
            else:
                x2 = dist[rrest[cig[0]]-1][rrest[cig[1]]-1] # shift by 1
                
            dx.append(abs(x1-x2))
            
            
    # combine sugg with distance
    ranks = []
    for ig in range(len(sugg)):
        ranks.append(sugg[ig]*(np.exp(-dx[ig]**2/(2*5643.81**2))+0.00735612)) # fit from data
    
    ranks = np.array(ranks)
    
    # if not enough suggestions fill in by tips
    nc0 = sum(map(lambda x: x>0, ranks))
    nc1 = 0
    if ( nc0 < nc):
        nc1 = nc - sum(map(lambda x: x>0, ranks))
                       
        if (M==-1):
            conn = msc.mysqlcon()
            x = conn.cursor()
            
        x.execute('select good, tips from foursquare join foursquare_id on foursquare.id=foursquare_id.id order by nid');
        result = x.fetchall()
        
        #print 'res list ' + str(len(result))
        toplist_supp = [0]
        for jg in range(len(result)):            
            if (jg+1 in rrest):
              tipxdist = 0 # no repeats
            else:
              tipxdist = result[jg][0]*float(result[jg][1])*(np.exp(-dx[jg+1]**2/(2*5643.81**2))+0.00735612)
            toplist_supp.append(tipxdist)
    
    # combine the two top recommendation lists
    toplist = ranks.argsort()[-nc:][::-1]
    
    if ( nc0 < nc):
        toplist_supp = np.array(toplist_supp).argsort()[-nc:][::-1]
        if (M==-1):
            conn.close()
            x.close()
    
    #print toplist
    top5list = []
    for ig in range(min(nc0,nc)):
        top5list.append(toplist[ig])
    for ig in range(nc1):
        top5list.append(toplist_supp[ig])
        
    return top5list, dx

# this gets the top recommendations
def suggest(vin,origin,destination):
  
  conn = msc.mysqlcon()
  x = conn.cursor()
  
  # -----------    
  mcn=np.loadtxt('mcn.mat')
  dist=np.loadtxt('dx_mat.mat')
  
  #print vin
  if vin:
    vin = vin.split(',')
    vin = map(lambda x: int(x), vin)
  #top5, dxlist = top5dist(mcn,dist,vin,origin,destination)
  top5, dxlist = top5dist(mcn,dist,vin,origin,destination,-1,6)
  
  #top5s = str(top5[0]) + ', ' + str(top5[1]) + ', ' + str(top5[2]) + ', ' + str(top5[3]) + ', ' + str(top5[4])
  top5s = str(top5[0]) + ', ' + str(top5[1]) + ', ' + str(top5[2]) + ', ' + str(top5[3]) + ', ' + str(top5[4]) + ', ' + str(top5[5]) # now top 6
  top5s = 'select nid, lat, lng, name, url, photo from foursquare join foursquare_id on foursquare.id=foursquare_id.id where nid in (%s) ORDER BY FIND_IN_SET(nid,"%s")' % (top5s,top5s)
  x.execute(top5s); 
  result = x.fetchall() # need to sort by request order
  
  sites = []
  for res in result:
    
    # hours and minutes out of the way
    sf = 2 # scale factor
    dxin = dxlist[res[0]]*sf+3
    dxihm = '%02d:%02d' % (int(dxin/96500),int(dxin/96500 % 1 * 60))
    
    # distance out of the way (miles)
    #sf = 1 
    #dxihm = round( float(dxlist[res[0]])*sf/1000/0.621371,2)
    #dxihm = float(dxlist[res[0]]/1000)
    
    sites.append(dict(City=unicode(str(res[0]), 'utf8'), CountryCode=res[3], dxi=dxihm, lat=res[1], lng=res[2], url=res[4], photo=res[5] )) # nid, name, time off in HHMM
  
  try:
      x.close()
      conn.close()
  except:
      print "nothing to close"
      
  return sites

def main():
  print 'i do nothing'

if __name__ == '__main__':
  main()
