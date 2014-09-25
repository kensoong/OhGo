import os
from flask import render_template, request, flash, jsonify, Flask
import MySQLdb
import json
import re
import analytics as ant
import numpy as np
import mysqlconnect as msc
from mapquest_utils import *

app = Flask(__name__)

#db = msc.mysqlcon()

@app.route("/")
@app.route("/index")
@app.route("/landing")
def hello():
    return render_template('landing.html') 

# submit input and load itin picker    
@app.route("/choose", methods=["POST","GET"])
def testpost():

    origin = request.form["origin"]
    origin_name = origin
    destination = request.form["destination"]
    destination_name = destination
    roundtrip = request.form.get('roundtrip')
    if not roundtrip:
        roundtrip = 0
    
    # do rev geo here
    mquest=mapquest()
    s1latlng = mquest.revgeo(origin)
    e1latlng = mquest.revgeo(destination)
    
    origin = str(s1latlng[0]) + ',' + str(s1latlng[1])
    destination = str(e1latlng[0]) + ',' + str(e1latlng[1])
    
    return render_template('index_map.html',origin=origin, destination=destination, roundtrip=roundtrip, origin_name=origin_name, destination_name=destination_name) 


# return the current agenda
@app.route("/db_path/<vc>", methods=["GET"])
def path_json(vc):
    
    db = msc.mysqlcon()
    
    cities = []
    vc = vc.split(',')
    for vci in vc:    
        que = "select nid, name, lat, lng, url, photo from foursquare join foursquare_id on foursquare.id=foursquare_id.id where nid=%s" % vci
        db.query(que)
        query_results = db.store_result().fetch_row(maxrows=1)
        #print query_results
        
        for result in query_results:
            nname = result[1].encode('ascii','ignore')
            cities.append( dict(City=unicode(str(result[0]), 'utf8'), CountryCode=nname, lat=result[2], lng=result[3], url=result[4], photo=result[5]) )
    
    db.close()
    
    return jsonify(dict(cities=cities))

# suggestions based on route and sites
@app.route("/db_suggest/<vin>", methods=["GET"])
def sugg_json(vin):
    
    vin = vin.split('&')
    origin = vin[0]
    destination = vin[1]
    if len(vin)==2:
        vsites = []
    else:  
        vsites = vin[2]
    
    cities = ant.suggest(vsites,origin,destination)
    
    return jsonify(dict(cities=cities))    

@app.route('/slides')
def showslides(): 
    return render_template('slides.html') 

@app.route('/ken')
def ken(): 
    return render_template('ken.html') 
    
@app.route('/<pagename>') 
def regularpage(pagename=None): 
    """ 
    Route not found by the other routes above. May point to a static template. 
    """ 
    return "You've arrived at " + pagename

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
