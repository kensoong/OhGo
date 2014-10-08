import re
import urllib2
import MySQLdb
import json
import numpy as np
import mysqlconnect as msc

global nc 
nc = 6

def firstele(x):
    return x[0]

# return top N suggestions factoring in distance
def top5dist(mcn,dist,rone,rrest):
        
    sugg = mcn[0]-mcn[0]  
    for r in rrest:
        sugg += mcn[r]
    
    for r in rrest:
        sugg[r]=0
    
    # make NxM matrix of relevant distances
    dmat = []
    for rr in rrest:
        dmat.append(np.append(0,dist[rr-1]))
    dmat = np.array(dmat)
    
    # find closest points
    dx = [0]
    for ig in range(len(mcn)):
        if ig:
            closest = dmat[:,ig]
            cig = closest.argsort()[:2]
            x1 = closest[cig[0]]+closest[cig[1]]
            x2 = dist[rrest[cig[0]]-1][rrest[cig[1]]-1]
            dx.append(x1-x2)
    
    # combine sugg with distance
    ranks = []
    for ig in range(len(sugg)):
        ranks.append(sugg[ig]*(np.exp(-dx[ig]**2/(2*5643.81**2))+0.00735612)) # fit from data
    
    ranks = np.array(ranks)
    toplist = []
    toplist = ranks.argsort()[-nc:][::-1]
    
    return (rone in toplist)


def top5(mcn,rone,rrest):
    #nc = 5
    vout = mcn[0]-mcn[0]  
    for r in rrest:
        vout += mcn[r]
    
    for r in rrest:
        vout[r]=0
    
    toplist = []
    toplist = vout.argsort()[-nc:][::-1]
    
    return (rone in toplist)

def top5dumb(toplist,rone,rrest):
    #nc = 5
    
    # remove existing sites from prediction
    toplist2 = toplist[:]
    for r1 in rrest:
        if r1 in toplist:
            toplist2.remove(r1)
    
    toplist2 = toplist2[:nc]
    
    return (rone in toplist2)

conn = msc.mysqlcon()
x = conn.cursor()


# ---- dumb algorithm, top 5 ----- #
x.execute('select region from instagrams group by region order by count(region) desc')
result = x.fetchall()

dumb = []
for res in result:
    dumb.append(res[0])
    
# -----------    
mcn=np.loadtxt('mcn.mat')
dist=np.loadtxt('dx_mat.mat')

x.execute('select uid, count(distinct region) from instagrams_mult_new group by uid order by count(distinct region) desc')
result = x.fetchall()

# xck - smart algorith, xck2 - smart + distance, xckd - dumb
xck = [0 for ro in xrange(2)]
xckd = [xck[:] for co in xrange(result[0][1]+1)]
xck2 = [xck[:] for co in xrange(result[0][1]+1)]
xck = [xck[:] for co in xrange(result[0][1]+1)]


ni = 0
for res in result:
    ni+=1
    if not ni%1000:
      print str(ni) + '/' + str(lenres)

    x.execute('select distinct region from instagrams_mult_new where uid=%s',(res[0],))
    regions = x.fetchall()
    
    for ri in range(len(regions)):
        reg1 = regions[ri][0]
        reg2 = regions[:ri] + regions[ri+1:]
        reg2 = map(firstele, reg2)
        
        # smart
        xck[len(regions)][1] += 1
        if top5(mcn,reg1,reg2):
            xck[len(regions)][0] += 1
        
        # smart + dist
        xck2[len(regions)][1] += 1
        if (len(reg2) > 1):
            if top5dist(mcn,dist,reg1,reg2):
                xck2[len(regions)][0] += 1
        else:
            if top5(mcn,reg1,reg2):
                xck2[len(regions)][0] += 1            
        # dumb
        xckd[len(regions)][1] += 1
        if top5dumb(dumb,reg1,reg2):
            xckd[len(regions)][0] += 1

# hit rate
print 'algorithm hit rate'
print 'sites', 'hit rate'
pxck = []
counter = 0
for xc in xck:
    if xc[1]==0:
        xc[1]+=1
    print counter, float(xc[0])/xc[1]
    pxck.append(float(xc[0])/xc[1])
    counter += 1

print '\n'

# hit rate + distance
print 'algorithm+dist hit rate'
print 'sites', 'hit rate'
pxck2 = []
counter = 0
for xc in xck2:
    if xc[1]==0:
        xc[1]+=1
    print counter, float(xc[0])/xc[1]/(pxck[counter]+0.000000000000001) # work around for divide by zero
    pxck2.append(float(xc[0])/xc[1])
    counter += 1

print '\n'

# hit rate using dumb method
pxkcd = []
for xc in xckd:
    if xc[1]==0:
        xc[1]+=1
    pxkcd.append(float(xc[0])/xc[1])

print 'smart hit rate / top 5 suggestions'
print 'sites', 'rel. hit rate'
for x1 in range(len(xck)):
    if pxkcd[x1]==0:
        pxkcd[x1] += 1    
    print x1, pxck[x1]/pxkcd[x1]

print '\n'

# random suggestions
print 'smart hit rate / random suggestions'
print 'sites', 'rel. hit rate'
counter = 0
for x1 in range(len(xck)): 
    prand = float(x1)/(83-x1)
    if prand == 0:
        prand = 1
    print counter, pxck[x1]/prand
    counter += 1
