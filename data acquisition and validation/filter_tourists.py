# this just makes a new table with all the users who have multiple locations aka tourists

import os
import sys
import MySQLdb  # pip install MySQL-python
import mysqlconnect as msc

conn = msc.mysqlcon()
x = conn.cursor()


# put all users who have multiple photos in one table
x.execute('SELECT uid FROM instagrams GROUP BY uid HAVING count(distinct region) > 1;')
result = x.fetchall()

tres = ''
ncnt = 0
for res in result:   
  ncnt += 1
  tres += res[0] + ','
  
  if not ncnt % 100:
    print ncnt
    tres = tres[:-1]      
    sqltxt = 'INSERT instagrams_mult SELECT * FROM instagrams where uid in (%s);' % (tres)  
    x.execute(sqltxt)   
    conn.commit()
    tres = ''

tres = tres[:-1]      
sqltxt = 'INSERT instagrams_mult SELECT * FROM instagrams where uid in (%s);' % (tres)  
x.execute(sqltxt)   
conn.commit()
tres = ''

x.close()
conn.close()

