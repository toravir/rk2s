# rk2s (RunKeeper 2 Strava)

rk2s is a python script that uploads runkeeper activities to strava.

runkeeper does not export clear APIs like strava does - so runkeeper activities need to 
downloaded as .zip file and provided as an input to this tool.

The steps involved are:

0. Download activities as a zip file from runkeeper
1. Visit http://employees.org/~ravir/play/rk2s/rk2s.html to get access token and refresh token
   This is starting page to give permissions to strava account
2. Run this tool with the access and refresh tokens and the zip file 


## Usage:

```
python rk2s.py [-h] --atok ATOK --rtok RTOK --zip ZIP [--delay DELAY]

-h : Prints the help/Usage
--atok : provide the access token
--rtok : provide the refresh token
--zip  : ZIP file downloaded from runkeeper.com
--delay : delay in seconds (default 10s) between consecutive uploads to strava
```

If OTOH, you are using the docker containers, use:
```
docker run -it -v `pwd`:/cwd rravir/rk2s:latest [-h] --atok ATOK --rtok RTOK --zip ZIP [--delay DELAY]
```
The volume mapping is needed to access to the zip file from within the container.

## Requirements:
TL;DR: Use Docker to download the prebuilt container image from https://hub.docker.com/r/rravir/rk2s
Dockerfile included specifies all the needed dependencies - if u wish to install them on your own machine or
build your own docker image.


### Long Version
Strava APIs are published in a swagger.json (https://developers.strava.com/swagger/swagger.json).
You need to download it and use swagger codegen to generate python client api library. In addition to
that there are a bunch of requirements that code-gen output requires plus rk2s.py requires requests and other
python packages too. Skim the Dockerfile for the various steps all these dependencies are setup.

## Examples

```
> docker run -it -v `pwd`:/cwd t1 --atok a36d8868038cfa328984278648660b05baf85c78 --rtok a4a0910ba93d5a810b465e8a12e1c45c041f0f1e --zip tc2/tc2.zip
Welcome to Run Keeper 2 Strava Tool - Please start from

http://employees.org/~ravir/play/rk2s/rk2s.html


Uploading activities from:/cwd/tc2/tc2.zip
Extract zip file into  /tmp/tmpDGMUU8
Uploading: 563d1497-0c7b-4f4b-822f-42a6fed8fb49 2011-08-06T13:18:15Z Ride 21992.6 3174 /tmp/tmpDGMUU8/2011-08-06-131815.gpx
token has Expired.. Refreshing token..
Uploading: 457ffc85-c60a-4a0b-a3ca-9ddd46950db6 2011-08-04T08:27:56Z Run 6343.4 2171 /tmp/tmpDGMUU8/2011-08-04-082756.gpx
> 
```


## Limitations
1. Error conditions are not handled well - it will just crash and burn.
2. Mapping of Runkeeper Activities Types to Strava Activity Types are limited to - more can be added - but i don't know
what are possible activity types in Runkeeper.
```
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
```
3. I don't have enough test inputs (except my own) to verify - i have included two testcases in the repo:
   tc1/tc1.zip - has manual activities without any GPX
   tc2/tc2.zip - has GPX based activities
4. Strava Activity cannot be set to be private or public during the upload - if this is needed, please open
and issue and i can look into how to set that.

