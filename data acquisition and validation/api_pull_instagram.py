# this pulls data from instagram
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import re
import sys
import urllib
import urllib2
import MySQLdb
import json
import mysqlconnect as msc
import keys as keys

def parser(lat,lng,dist,region,ctime='1410720504'):
  global conn
  global x

  url1 = 'https://api.instagram.com/v1/media/search?client_id=' + keys.instagram + '&lat=' + str(lat) + '&lng=' + str(lng) + '&distance=' + str(dist) + '&max_timestamp='
  url1 += ctime
  data = json.load(urllib2.urlopen(url1))
  print url1

  if data['meta']['code'] == 200 and data['data']:
    x1 = []
    y1 = []
    for ig in range(len(data['data'])):
      try:
        pid = data['data'][ig]['id']
        ctime = data['data'][ig]['created_time']
        lat = data['data'][ig]['location']['latitude']
        lng = data['data'][ig]['location']['longitude']
        try: 
          lname = data['data'][ig]['location']['name']
        except:
          lname = 'none'
        likes = data['data'][ig]['likes']['count']
        tags = ','.join(data['data'][ig]['tags'])
        tags = tags.encode('ascii','ignore')
        
        link = data['data'][ig]['link']
        uid = data['data'][ig]['user']['id']

        #print '(' + str(lat) + ',' + str(lng) + ')'

        x1.append(lat)
        y1.append(lng)
        if not in_tb(pid):
          insert = 'INSERT into instagrams_id (id) VALUES (%s)'
          x.execute(insert,(pid,))
          insert = '''
            INSERT into instagrams 
            (id, ctime, lat, lng, lname, likes, tags, link, uid, region) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            '''
          
          #x.execute(insert,(pid,ctime,float(lat),float(lng),lname,int(likes),tags,link,uid,region))
          x.execute(insert,(pid,ctime,lat,lng,lname,likes,tags,link,uid,region))
        
        else:
          print "already done that"
      except:
        print "something went wrong with " + data['data'][ig]['id']
      
    #plt.plot(x1,y1,'rx')
    #plt.show()
    ok = 1
  else:
    print 'something bad happened with the API. meta code ' + str(data['meta']['code'])
    ok = 0
    
  return ok

def in_tb(pid):
  global x
  
  fc = 'SELECT id FROM instagrams_id WHERE id=%s'
  x.execute(fc,(pid,))
  outp = x.fetchall()  
  
  #print outp
  #print outp[0][0]
  return outp

# open MySQL connection
def open_mysql():
  global conn
  global x
  
  conn = msc.mysqlcon()
  x = conn.cursor()
  
def main():
  global conn
  global x

  args = sys.argv[1:]

  if not args:
    print 'usage: lat, lng, dist, region'
    sys.exit(1)
  
  lat = args[0]
  lng = args[1]
  dist = args[2]
  region = args[3]  

  open_mysql()
  
  # call the instagram API
  parser(lat,lng,dist,region)
  conn.commit()
  
  print 'got thru 1'
  
  outp1 = 0
  ok = 1
  n1 = 0
  nrp = 0;
  while ok:
    fc = 'SELECT min(ctime) FROM instagrams where region=%s'
    x.execute(fc,(region,))
   
    outp = x.fetchall() 
 
    outp = str(float(outp[0][0]) - 1);
    
    # see if it goes into an inf loop
    if outp1 == outp:
      print "WARNING SAME CTIME DETECTED"
      outp = str(float(outp)-10)
      nrp += 1
      
    outp1 = outp  

    ok = parser(lat,lng,dist,region,outp)
    n1 += 1
    
    print 'iteration ' + str(n1) + ' time min = ' + str(outp) 

    conn.commit()
    
    # break if no new data is available
    if nrp > 10:
      ok = 0
              
    if float(outp) < 1408000000.0:
      ok = 0
      print 'time limit = 1 month'
    
if __name__ == '__main__':
  main()
