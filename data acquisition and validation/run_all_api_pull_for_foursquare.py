# this pulls data for all instagrams within the list of landmarks

import os
import sys
import MySQLdb
import mysqlconnect as msc

conn = msc.mysqlcon()
x = conn.cursor()

x.execute('select nid, lat, lng, dist, name from foursquare join foursquare_id on foursquare.id=foursquare_id.id where good = 1 order by tips desc')
result = x.fetchall()

for res in result:
  print 'python api_pull_instagram.py ' + str(res[1]) + ' ' + str(res[2]) + ' ' + str(res[3]) + ' ' + str(res[0])
  os.system('python api_pull_instagram.py ' + str(res[1]) + ' ' + str(res[2]) + ' ' + str(res[3]) + ' ' + str(res[0]))

# back up the tables in case of accidents later
x.execute('DROP TABLE IF EXISTS instagrams_full_copy')
x.execute('create table instagrams_full_copy like instagrams')
x.execute('INSERT instagrams_full_copy SELECT * FROM instagrams')

x.execute('DROP TABLE IF EXISTS instagrams_id_full_copy;')
x.execute('create table instagrams_id_full_copy like instagrams_id')
x.execute('INSERT instagrams_id_full_copy SELECT * FROM instagrams_id')
