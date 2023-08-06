#!/usr/bin/python
#coding: utf-8
# @author Xavier Orduña (xorduna@dexmatech.com)
#Copyright (c) 2012, Dexma Sensors S.L.
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Dexma Sensors S.L. nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#DISCLAIMED. IN NO EVENT SHALL Dexma Sensors S.L. BE LIABLE FOR ANY
#DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import urllib2
import json
from datetime import datetime, timedelta
import re, urllib
import logging

def _json_date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def _datetime_parser(dct):
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
    for k, v in dct.items():
        if isinstance(v, basestring) and re.search("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", v):
            try:
                dct[k] = datetime.strptime(v, DATE_FORMAT)
            except:
                pass
    return dct    

class DRapiException(Exception):
    def __init__(self, error_type, description, info):
        self.type = error_type
        self.description = description
        self.info = info
    def __str__(self):
        return repr(self.type + ":" + self.description + "(" + self.info + ")")

class DRapiOAuth(object):
    
    def __init__(self, endpoint, hash, secret, logger=None):
        self.endpoint = endpoint
        self.hash = hash
        self.secret = secret
        if logger != None:
            self.logger = logger
        else:
            self.logger = logging.getLogger('drapi')
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(logging.NullHandler())
    
    def __call_rest(self, url):
        url = self.endpoint + url
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        data = response.read()
        self.logger.info(data)
        return data
    
    #needed ?
    def oauth_redirect(self, temp_token):
        url = "/oauth/access_token?code="+str(temp_token)+"&client_secret="+self.secret+"&client_id="+self.hash
        #print self.__call_rest(url)
    
    def perm_token(self, temp_token):
        url = "/oauth/accesstoken?temp_token="+str(temp_token)+"&secret="+self.secret+"&idclient="+self.hash
        response = self.__call_rest(url)
        return response

    def setThing(self, key, value):
        url = self.endpoint + "/things/set/" + key
        req = urllib2.Request(url, json.dumps(value, default=_json_date_handler), headers={'x-dexcell-secret': self.secret})
        self.logger.info('storing key: '+key+' with secret: '+self.secret)
        response = urllib2.urlopen(req)
        data = response.read()
        return data
    
    def getThing(self, key):
        url = self.endpoint + "/things/get/" + key
        req = urllib2.Request(url, headers={'x-dexcell-secret': self.secret})
        response = urllib2.urlopen(req)
        data = response.read()
        data = json.loads(data, object_hook=_datetime_parser)
        result = json.loads(data['result'], object_hook=_datetime_parser)
        return result

class DRapi(object):
    '''
    classdocs
    '''

    def __init__(self, endpoint, token, logger=None):
        '''
        Constructor
        '''
        self.endpoint = endpoint
        self.token = token
        if logger != None:
            self.logger = logger
        else:
            self.logger = logging.getLogger('drapi')
            self.logger.setLevel(logging.DEBUG)
    
    def dxdate(self, dt):
        return dt.strftime("%Y%m%d%H%M%S")
    
    def __call_rest(self, url, payload=None, parse_response=True):
        url = self.endpoint + url
        self.logger.info('url:'+url+' token:'+self.token)
        print url, self.token
        if payload == None:
            req = urllib2.Request(url, headers={'x-dexcell-token': self.token})
        else:
            req = urllib2.Request(url, payload, headers={'x-dexcell-token': self.token})
        #error verification
        try:
            response = urllib2.urlopen(req)
            data = response.read()
            if parse_response:
                return json.loads(data)
            else:
                return data
        except urllib2.HTTPError as httperror:

            info = json.loads(httperror.read())
            
            if httperror.code == 404:
                self.logger.error('error: not found')
                raise DRapiException('NOTFOUND', info['description'], info['moreInfo'])
            elif httperror.code == 401:
                self.logger.error('error: not authorized')
                raise DRapiException('INVALIDTOKEN', info['description'], info['moreInfo'])
            else:
                raise DRapiException('UNKNOWN', info['description'], info['moreInfo'])
                self.logger.error('error: ' + str(httperror.code))
    
    def getLocation(self, loc_id):
        location = self.__call_rest("/locations/" + str(loc_id) + ".json")
        return location
    
    def getDeploymentLocations(self, dep_id):
        location_list = self.__call_rest("/deployments/"+str(dep_id)+"/locations.json")
        return location_list

    def getDeploymentDevices(self, dep_id):
        device_list = self.__call_rest("/deployments/"+str(dep_id)+"/devices.json")
        return device_list
    
    def getDeploymentParameters(self, dep_id):
        param_list = self.__call_rest("/deployments/"+str(dep_id)+"/parameters.json")
        return param_list
    
    def getDeploymentSupplies(self, dep_id):
        supply_list = self.__call_rest("/deployments/"+str(dep_id)+"/supplies.json")
        return supply_list
    
    def getDeploymentNotices(self, dep_id, start, end):
        notice_list = self.__call_rest("/deployments/"+str(dep_id)+"/notices.json?start="+self.dxdate(start)+"&end="+self.dxdate(end))
        return notice_list
    
    def getLocationParameters(self, loc_id):
        param_list = self.__call_rest("/locations/"+str(loc_id)+"/parameters.json")
        return param_list

    def getLocationNotices(self, loc_id, start, end):
        notice_list = self.__call_rest("/locations/"+str(loc_id)+"/notices.json?start="+self.dxdate(start)+"&end="+self.dxdate(end))
        return notice_list
    
    def getLocationSimulatedBill(self, loc_id, start, end):
        bill = self.__call_rest("/locations/"+str(loc_id)+"/simulatedbill.json?start="+self.dxdate(start)+"&end="+self.dxdate(end))
        return bill    
    
    def getDeviceParameters(self, dev_id):
        param_list = self.__call_rest("/devices/"+str(dev_id)+"/parameters.json")
        return param_list
    
    def getLocationParameterDevices(self, loc_id, param_nid):
        device_list = self.__call_rest("/locations/"+str(loc_id)+"/parameters/"+str(param_nid)+"/devices.json")
        return device_list
    
    def getDeploymentParameterDevices(self, dep_id, param_nid):
        device_list = self.__call_rest("/deployments/"+str(dep_id)+"/parameters/"+str(param_nid)+"/devices.json")
        return device_list
                
    def getLocationSupplies(self, loc_id):
        supply_list = self.__call_rest("/locations/"+str(loc_id)+"/supplies.json")
        return supply_list
        
    def getLocationDevices(self, loc_id):
        device_list = self.__call_rest("/locations/"+str(loc_id)+"/devices.json")
        return device_list
    
    def getDeployment(self, dep_id):
        deployment = self.__call_rest("/deployments/"+ str(dep_id) + ".json")
        return deployment
    
    def getDevice(self, dev_id):
        device = self.__call_rest("/devices/" + str(dev_id) + ".json")
        return device

    def getSupplyBills(self, sup_id, start, end, tolerance=0):
        bills = self.__call_rest("/supplies/" + str(sup_id) + "/bills.json?start="+self.dxdate(start)+"&end="+self.dxdate(end))
        return bills

    def session(self, session_id):
        url = "/session/" + session_id + ".json"
        response = self.__call_rest(url)
        self.logger.info('get session: '+str(response))
        return response
    
    def setDeploymentThing(self, dep_id, key, value):
        url = "/deployments/"+str(dep_id)+"/things/set/" + key + ".json"
        payload = json.dumps(value, default=_json_date_handler)
        data = self.__call_rest(url, payload=payload, parse_response=False)
        return data
        
    def getDeploymentThing(self, dep_id, key):
        url = "/deployments/"+str(dep_id)+"/things/get/" + key + ".json"
        data = self.__call_rest(url, parse_response=False)
        self.logger.info('depthing:' + str(data))
        data = json.loads(data, object_hook=_datetime_parser)
        return data
    
    def getReadings(self, dev_id, snid, start, end):
        url = "/devices/"+str(dev_id)+"/"+str(snid)+"/readings.json?start="+self.dxdate(start)+"&end="+self.dxdate(end)
        readings = self.__call_rest(url)
        for i in range(0, len(readings)):
            try:
                readings[i]['ts'] = datetime.strptime(readings[i]['ts'], "%Y-%m-%d %H:%M:%S")
                readings[i]['tsutc'] = datetime.strptime(readings[i]['tsutc'], "%Y-%m-%d %H:%M:%S")
            except KeyError:
                pass
        return readings

    def getReadingsNew(self, dev_id, param, frequency, operation, start, end):
        url = "/devices/"+str(dev_id)+"/"+str(param)+"/readings.json?start="+self.dxdate(start)+"&end="+self.dxdate(end)+"&frequency="+str(frequency)+"&operation="+str(operation)
        readings = self.__call_rest(url)
        for i in range(0, len(readings)):
            try:
                readings[i]['ts'] = datetime.strptime(readings[i]['ts'], "%Y-%m-%d %H:%M:%S")
                readings[i]['tsutc'] = datetime.strptime(readings[i]['tsutc'], "%Y-%m-%d %H:%M:%S")
            except KeyError:
                pass
        return readings

    def getCost(self, nid, start, end, energytype = 'ELECTRICAL', period='HOUR', grouped=False):
        str_grouped = 'TRUE'
        if grouped: str_grouped = 'FALSE'
        url = "/devices/"+str(nid)+"/"+str(energytype)+"/cost.json?start="+self.dxdate(start)+"&end="+self.dxdate(end)+"&period="+str(period)+"&grouped="+str_grouped
        raw_response = self.__call_rest(url)
        try:
            readings = raw_response['readings']
            for i in range(0, len(readings)):
                #readings[i]['ts'] = datetime.strptime(readings[i]['ts'], "%Y-%m-%d %H:%M:%S")
                #readings[i]['ts'] = datetime.strptime(readings[i]['ts'], "%Y/%m/%d %H:%M")
                readings[i]['ts'] = datetime.strptime(readings[i]['ts'], "%Y-%m-%d %H:%M:%S")
            
            periods = raw_response['periods']
            return readings, periods
        except KeyError:
            return []
            
        