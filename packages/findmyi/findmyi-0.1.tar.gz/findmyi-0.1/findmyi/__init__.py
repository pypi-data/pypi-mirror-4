import requests
from base64 import b64encode
import json
import time


class FMI(object):
    def __init__(self, user, password):
        self.user = user
        self.authToken = b64encode("%s:%s" % (user, password))
        self.devices = []
        self.host = ""
        self.getPartition()

    def getPartition(self):
        data = {
            'clientContext': {
                'appName': 'FindMyiPhone',
                'appVersion': '1.4',
                'buildVersion': '145',
                'deviceUDID': '0000000000000000000000000000000000000000',
                'inactiveTime': 5911,
                'osVersion': '4.2.1',
                'personID': 0,
                'productType': 'iPad1,1'
            }
        }

        url = "https://fmipmobile.icloud.com:443/fmipservice/device/%s/initClient" % (self.user)
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Apple-Find-Api-Ver': '2.0',
            'X-Apple-Authscheme': 'UserIdGuest',
            'X-Apple-Realm-Support': '1.2',
            'User-Agent': 'Find iPhone/1.4 MeKit (iPad: iPhone OS/4.2.1)',
            'X-Client-Name': 'iPad',
            'X-Client-Uuid': '0cf3dc501ff812adb0b202baed4f37274b210853',
            'Accept-Language': 'en-us',
            'Authorization': "Basic %s" % (self.authToken)
        }

        req = requests.Session()
        req.headers = headers
        try:
            res = req.post(url, json.dumps(data))
            host = res.headers['X-Apple-MMe-Host']
        except:
            print "error"
        self.host = host

    def updateDevice(self):
        data = {
            'clientContext': {
                'appName': 'FindMyiPhone',
                'appVersion': '1.4',
                'buildVersion': '145',
                'deviceUDID': '0000000000000000000000000000000000000000',
                'inactiveTime': 5911,
                'osVersion': '4.2.1',
                'personID': 0,
                'productType': 'iPad1,1'
            }
        }
        deviceString = self.makeRequest("initClient", data)["content"]
        for device in deviceString:
            deviceDict = {}
            deviceDict['id'] = device['id']
            deviceDict['battery'] = device['batteryLevel'] * 100
            deviceDict['name'] = device['name']
            deviceDict['model'] = device['deviceModel']
            deviceDict['displayName'] = device['deviceDisplayName']
            if device['location']:
                deviceDict['latitude'] = device['location']['latitude']
                deviceDict['longitude'] = device['location']['longitude']
                deviceDict['updateTime'] = device['location']['timeStamp']
                deviceDict['positionType'] = device['location']['positionType']
                deviceDict['accuracy'] = device['location']['horizontalAccuracy']
            self.devices.append(deviceDict)

    def makeRequest(self, method, data):
        url = "https://%s/fmipservice/device/%s/%s" % (self.host, self.user, method)

        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'X-Apple-Find-Api-Ver': '2.0',
            'X-Apple-Authscheme': 'UserIdGuest',
            'X-Apple-Realm-Support': '1.2',
            'User-Agent': 'Find iPhone/1.4 MeKit (iPad: iPhone OS/4.2.1)',
            'X-Client-Name': 'iPad',
            'X-Client-Uuid': '0cf3dc501ff812adb0b202baed4f37274b210853',
            'Accept-Language': 'en-us',
            'Authorization': "Basic %s" % (self.authToken)
        }

        req = requests.Session()
        req.headers = headers
        repsonseString = ""
        res = req.post(url, json.dumps(data))
        while repsonseString == "":
            try:
                res = req.post(url, json.dumps(data))
                repsonseString = res.json
            except:
                print "e"
                time.sleep(30)
        return repsonseString

    def sendMessage(self, deviceNum, subject, message, sound=True):
        deviceID = self.devices[deviceNum]['id']
        if sound:
            alarm = "true"
        else:
            alarm = "false"
        data = {
            'clientContext': {
                'appName': 'FindMyiPhone',
                'appVersion': '1.4',
                'buildVersion': '145',
                'deviceUDID': '0000000000000000000000000000000000000000',
                'inactiveTime': 5911,
                'osVersion': '4.2.1',
                'personID': 0,
                'productType': 'iPad1,1',
                'selectetDevice': deviceID,
                'shouldLocate': 'false'
            },
            'device': deviceID,
            'serverContext': {
                "callbackIntervalInMS": 3000,
                "clientId": "0000000000000000000000000000000000000000",
                "deviceLoadStatus": "203",
                "hasDevices": "true",
                "lastSessionExtensionTime": "null",
                "maxDeviceLoadTime": 60000,
                "maxLocatingTime": 90000,
                "preferredLanguage": "en",
                "prefsUpdateTime": 1276872996660,
                "sessionLifespan": 900000,
                "timezone": {
                    "currentOffset": -25200000,
                    "previousOffset": -28800000,
                    "previousTransition": 1268560799999,
                    "tzCurrentName": "Pacific Daylight Time",
                    "tzName": "America/Los_Angeles"
                },
                "validRegion": "true"
            },
            'sound': alarm,
            'subject': subject,
            'text': message,
            'userText': "true"
        }
        self.makeRequest("sendMessage", data)
