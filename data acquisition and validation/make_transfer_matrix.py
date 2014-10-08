import os
import sys
import MySQLdb 
import itertools as itt
import numpy as np
import mysqlconnect as msc

conn = msc.mysqlcon()
x = conn.cursor()

x.execute('select max(region) from instagrams_mult');
mcsize = x.fetchall()
mcsize = mcsize[0][0]+1

# make NxN matrix
mc = [0 for ro in xrange(mcsize)]
mc = [mc[:] for co in xrange(mcsize)]

x.execute('select distinct uid from instagrams_mult')
result = x.fetchall()
lenres = len(result)

ni = 0
for res in result:
    ni+=1
    if not ni%1000:
      print str(ni) + '/' + str(lenres)

    x.execute('select distinct region from instagrams_mult where uid=%s',(res[0],))
    regions = x.fetchall()
    
    perms  = itt.permutations(regions,2)
      
    for p in perms:
        mc[p[0][0]][p[1][0]] += 1    
        mc[p[1][0]][p[0][0]] += 1

x.close()
conn.close()
# save the non-normalized for easy of adding new data
np.savetxt('mc.mat', mc)

# now normalize
mc2 = np.loadtxt('mc.mat')

mc3 = [0 for ro in xrange(len(mc2))]
mc3 = [mc3[:] for co in xrange(len(mc2[0]))]

for m1 in range(len(mc2)):
    smc = sum(mc2[m1])
    if smc:
        for n1 in range(len(mc2[m1])):
            mc3[m1][n1] = mc2[m1][n1]/sum(mc2[m1])
            
np.savetxt('mcn.mat', mc3)
