from __future__ import print_function
import tempfile
import zipfile
import csv
import time
import datetime
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint
import requests
import json
import sys
import argparse
import os

METERS_PER_MILE=1610
delayBetweenUploads=10

def extractZipFile(zipfn):
    tmpDirname=tempfile.mkdtemp()
    print("Extract zip file into ", tmpDirname)

    with zipfile.ZipFile(zipfn, 'r') as zipfd:
        zipfd.extractall(tmpDirname)

    return (tmpDirname)

#Map of RK Activity type to strava type
stravaActType = {
        "Cycling" : "Ride",
        "Hiking" : "Hike",
        "Elliptical" : "Elliptical",
        "Circuit Training" : "Workout",
        "Meditation" : "Yoga",
        "Other" : "Workout",
        "Rowing" : "Rowing",
        "Running" : "Run",
        "Spinning" : "Ride",
        "Stairmaster / Stepwell" : "Workout",
        "Strength Training" : "WeightTraining",
        "Walking" : "Walk",
        "Yoga" : "Yoga",
        }


def parseAndUploadActivities(dirname, fname, upload=True):
    dirname=dirname+"/"
    fname=dirname+fname
    with open(fname) as csvfile:
        rowRdr = csv.reader(csvfile)
        isFirstLine=True
        for i in rowRdr:
            if isFirstLine:
                isFirstLine=False
                continue
            time.sleep(delayBetweenUploads)
            actId = i[0]
            date = i[1]
            date = date.replace(' ', 'T')
            date = date+"Z"
            actType = i[2]
            actDist = float(i[4]) * METERS_PER_MILE
            durStr = i[5]
            if durStr.count(':') == 2 :
                x = time.strptime(durStr, '%H:%M:%S')
            elif durStr.count(':') == 1:
                x = time.strptime(durStr, '%M:%S')
            else:
                x = time.strptime(durStr, '%S')

            durSec = datetime.timedelta(
                                hours=x.tm_hour, 
                                minutes=x.tm_min, 
                                seconds=x.tm_sec)
            durSec = int(durSec.total_seconds())
            gpxFilename = i[13]
            if gpxFilename != '':
                gpxFilename = dirname+gpxFilename

            newActType = "Workout"
            if actType in stravaActType.keys():
                newActType = stravaActType[actType]

            print("Uploading:", actId, date, newActType, actDist, durSec, gpxFilename)
            description='RK Activity Id:'+actId
            if not upload:
                continue

            tok = getAccessToken()

            if gpxFilename == '':
                uploadManualActivity(
                                tok,
                                newActType,
                                name="RK("+actType+")",
                                startDate=date,
                                durationSec=durSec,
                                descr=description,
                                distanceMtrs=actDist)
            else:
                uploadGpxActivity (
                        tok, 
                        gpxFileName=gpxFilename, 
                        name="RK("+actType+")", 
                        descr=description)


def uploadManualActivity (
                            tok, 
                            acttype, 
                            name, 
                            startDate, 
                            durationSec, 
                            descr, 
                            distanceMtrs):

    api_instance = swagger_client.ActivitiesApi()
    api_instance.api_client.configuration.access_token = tok
    api_instance.api_client.set_default_header('Content-Type', 'application/x-www-form-urlencoded')
    try:
        api_response = api_instance.create_activity(
                                name, 
                                acttype, 
                                startDate, 
                                durationSec, 
                                description=descr, 
                                distance=distanceMtrs, 
                                trainer=0, 
                                commute=0)
        return True
    except ApiException as e:
        print("Exception when calling ActivitiesApi->createActivity: %s\n" % e)
        return False


def uploadGpxActivity (
                        tok, 
                        gpxFileName, 
                        name, 
                        descr):

    api_instance = swagger_client.UploadsApi()
    api_instance.api_client.configuration.access_token = tok
    try:
        api_response = api_instance.create_upload(
                        file=gpxFileName, 
                        name=name, 
                        description=descr, 
                        trainer=0, 
                        commute=0, 
                        data_type='gpx', 
                        external_id='12345678912345')
        return True
    except ApiException as e:
        print("Exception when calling ActivitiesApi->createActivity: %s\n" % e)
        return False


#Test calls to functions
#parseAndUploadActivities("unzip", "tst.csv", upload=False)

currAccTok={}

def getAccessToken():
    clientId='43847'
    #Use your correct Secret here - the secret below is not the exact one..
    clientSec='59601952bd1d6a0774cfc8bd51cdf65f51'
    if currAccTok['expires_at']-int(time.time()) < 0:
        print("token has Expired.. Refreshing token..")
        refreshTok=currAccTok['refresh_token']
        r = requests.post('https://www.strava.com/api/v3/oauth/token?client_id='+clientId+'&client_secret='+clientSec+'&grant_type=refresh_token&refresh_token='+refreshTok)
        if r.status_code != 200:
            print("Token Refresh Failed :"+r.text)
            print("Bailing out - nothing more can be done - may be you haven't put in the correct clientSecret ??")
            sys.exit(1)
        resp=json.loads(r.text)
        currAccTok['token']=resp['access_token']
        currAccTok['refresh_token']=resp['refresh_token']
        currAccTok['expires_at']=resp['expires_at']

    return currAccTok['token']

def test_getAccessToken():
    currAccTok['refresh_token']='a4a0910ba93d5a810b465e8a12e1c45c041f0f1e'
    currAccTok['expires_at']=0
    print(getAccessToken())
    time.sleep(30)
    print(getAccessToken())


def parseArgs():
    desc='Tool to migrate Runkeeper activities to Strava'
    desc+='\n please start by visiting: \n'
    desc+='http://employees.org/~ravir/play/rk2s/rk2s.html \n'

    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--atok', help='Access Token', required=True)
    parser.add_argument('--rtok', help='Refresh Token', required=True)
    parser.add_argument(
                '--zip', 
                help='Zip file downloaded from Runkeeper', 
                required=True)
    parser.add_argument(
                '--delay', 
                help='delay between uploads (in secs) - default 10s', 
                default=10, 
                required=False, 
                type=int)

    args = parser.parse_args()
    currAccTok['expires_at']=0
    currAccTok['token']=args.atok
    currAccTok['refresh_token']=args.rtok
    delayBetweenUploads=args.delay
    if not os.path.isfile(args.zip):
        if os.path.isfile("/cwd/"+args.zip):
            args.zip="/cwd/"+args.zip
        else:
            print("Zip file "+args.zip+": is not accessible. Please make sure it is in current directory or any of it sub directory.")

    return args.zip

def main():
    print("Welcome to Run Keeper 2 Strava Tool - Please start from\n")
    print("http://employees.org/~ravir/play/rk2s/rk2s.html\n\n\n")
    zipFile = parseArgs()
    print("Uploading activities from:" + zipFile)
    unzipDir=extractZipFile(zipFile)
    parseAndUploadActivities(unzipDir, "cardioActivities.csv")


if __name__ == "__main__":
    main()

