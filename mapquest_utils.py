import urllib
import urllib2
import json
import requests
import re
from operator import add
from keys import keys

class mapquest():
    
    def __init__(self):
        self.key = keys.mapquestapi

    def revgeo(self,addr):
        
        url1 = 'http://www.mapquestapi.com/geocoding/v1/address?key=' + self.key + '&callback=renderOptions&inFormat=kvp&outFormat=json&location='
        
        url2 = addr.replace(' ', '%20') 
        url3 = url1 + url2
        data = urllib2.urlopen(url3).read()
        result = re.findall(r'"latLng":{"lat":(.*?),"lng":(.*?)}',data)
        
        return result[0]

    def get_optmroute(self,wayto):
        url = "http://open.mapquestapi.com/directions/v2/optimizedroute?key=" + self.key
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        
        route = {"locations":[]}
        
        for way in wayto:
            route['locations'].append( {"latLng":{"lat":way[0],"lng":way[1]}})

        r = requests.post(url, data=json.dumps(route), headers=headers)
        route_json = json.dumps(r.json(), indent=2)
        data = json.loads(route_json)
        
        #print data
        #return data
	return data['route']['locationSequence'] # returns the sequence of coordinates

    def onetoonedirections(self,start,end):
        url = 'http://www.mapquestapi.com/directions/v2/routematrix?key=' + self.key
        headers = {'content-type': 'application/json'}
        return requests.post(url, locations, headers=headers)
    

    def advanceddirections(self,start,end):
        url_base='http://www.mapquestapi.com/directions/v2/route?key='
        url_base=url_base+self.key
        
        
        url_mid='&ambiguities=ignore&avoidTimedConditions=false&doReverseGeocode=true&outFormat=json&routeType=fastest&timeType=1&enhancedNarrative=false&shapeFormat=raw&generalize=0&locale=en_US&unit=m&from='
        #start='Clarendon Blvd, Arlington, VA'
        url_mid2='&to='
        #end='2400 S Glebe Rd, Arlington, VA'
        url_end='&drivingStyle=1&highwayEfficiency=21.0'

        url_final=url_base + url_mid + start + url_mid2 + end + url_end
        url_final=url_final.replace(" ","%20")
        #print url_final
        return urllib2.urlopen(url_final)

    def onetomany(self,locations):
        #url_base=
        url = 'http://www.mapquestapi.com/directions/v2/routematrix?key=' + self.key
        headers = {'content-type': 'application/json'}
        return requests.post(url, locations, headers=headers)
        

    def timeoffroute(self,ricklist,startlist,endlist):
        #time off-route and distance along route
        strick=startlist+ricklist
        endrick=endlist+ricklist
        fidroute=startlist+endlist
        
        startjson=self.getonetomany(strick)
        endjson=self.getmanytoone(endrick)
        fidjson=self.getonetomany(fidroute)
        #print json.dumps(fidjson, indent=4, sort_keys=True)

        totaltime=map(add,startjson['time'],endjson['time'])
        fidtime=fidjson['time'][1]

        fiddist=fidjson['distance'][1]
        totaldist=startjson['distance']
        
        toffroute=[x-fidtime for x in totaltime]
        fracoffroute=[x/fiddist for x in totaldist]

        #Round-off and convert units

        toffroute=[0 if x<0 else x for x in toffroute]
        toffroute=[int(x/60. +0.5) for x in toffroute]  #convert to minutes

        fracoffroute=[float(int(x*100)) for x in fracoffroute]
        fiddist=int(10*fiddist)/10.

        start=[fidjson["locations"][0]["latLng"]["lat"],fidjson["locations"][0]["latLng"]["lng"]]
        end=[fidjson["locations"][-1]["latLng"]["lat"],fidjson["locations"][-1]["latLng"]["lng"]]

        locgmap=[]
        for i in range(1,len(startjson["locations"])):
            locgmap.append([startjson["locations"][i]["latLng"]["lat"],startjson["locations"][i]["latLng"]["lng"]])
        print "START = ",start,"END = ",end
        return toffroute,fracoffroute,fiddist,fidtime,start,end,locgmap


        
    def getonetomany(self,ricklist):

        locations = '{locations: '+str(ricklist)+', options: {allToAll:false}}'
        mapresponse = self.onetomany(locations)
	jsonmap = mapresponse.text

	jsonObj = json.loads(jsonmap)
	#print json.dumps(jsonObj, indent=4, sort_keys=True)
        return jsonObj

    def getmanytoone(self,ricklist):

        locations = '{locations: '+str(ricklist)+', options: {manyToOne:true}}'
        mapresponse = self.onetomany(locations)
	jsonmap = mapresponse.text

	jsonObj = json.loads(jsonmap)
	#print json.dumps(jsonObj, indent=4, sort_keys=True)
        return jsonObj



    ##################################################
if __name__=="__main__":
        
    mquest=mapquest()
    response=mquest.advanceddirections("kirkwood, ca","cupertino,ca")
    jsonobj=json.loads(response.read())
    print json.dumps(jsonobj, indent=4, sort_keys=True)
