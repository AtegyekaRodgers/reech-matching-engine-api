# Reech Python API

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/Reecheble2022/reech-python-api/tree/staging.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/Reecheble2022/reech-python-api/tree/staging)

Documentation: https://docs.google.com/document/d/1d75mh_wkSc9SaemS7g4izdzlDLT2KffL8kDE5CDFYYQ/edit?usp=sharing

## How to launch matching engine locally (steps for running):
These steps are also available here: https://realpython.com/python-web-applications/


#### 1 Navigate to /reech-python-api directory in terminal
#### 2 Set up a Python 3 virtual Env (Skip to 4 if done already)
    python3 -m venv venv
#### 3 Source virtual environment
##### 3.1 For linux
    source venv/bin/activate
##### 3.2 For windows
    .\venv\Scripts\activate
#### 4 Install package requirements by running this line in terminal (skip to 5 if done already):
    python3 -m pip install -r requirements.txt
#### 5 finally, launch the API:
    python3 matching_engine/launch.py

You will see the following output, note the local socket on line 6 (yours might be different):

    1. Serving Flask app 'main' (lazy loading) 
    2. Environment: production
    3. WARNING: This is a development server. Do not use it in a production deployment.
    4. Use a production WSGI server instead. 
    5. Debug mode: on 
    6. Running on http://<local socket> (Press CTRL+C to quit) 
    7. Restarting with stat 
    8. Debugger is active! 
    9. Debugger PIN: 869-010-228 
    
#### 7 Access the API 

The "local socket" is already displayed in the terminal - it is the url in line 6 mentioned above:

    6. Running on http://<local socket> (Press CTRL+C to quit)

Now, to access the various APIs, enter one of the following urls (potentially in a browser of your choice).

    http://<local socket>/
    http://<local socket>/home/reach_for/fetch/?request=<request>&n=<number>
    http://<local socket>/home/reach_for/response/?result=<request>&userID=<user ID>
    http://<local socket>/home/be_reached/fetch/?request=<request>&n=<number>
    http://<local socket>/home/be_reached/response/?result=<request>&userID=<user ID>
    http://<local socket>/bubble/fetch/?n=<number>

Examples:

    http://127.0.0.1:8080/home/reach_for/fetch/?request=engineer
    
    http://127.0.0.1:8080/home/be_reached/fetch/?request=engineer&n=7
    
    http://127.0.0.1:8080//bubble/fetch/?n=100


# Useful docs:
- https://pymongo.readthedocs.io/en/stable/atlas.html
- https://pymongo.readthedocs.io/en/stable/tutorial.html
- https://realpython.com/python-web-applications/

# Accessing MongoDB Atlas:
    https://cloud.mongodb.com/v2/62ddbe387eedc62af303cb1e#clusters
## gmail log in details:
### Username
    ree9350@gmail.com
### Password
    amazingDev!1

# MongoDB Community Server
 - Download the MSI for your system located at the link https://www.mongodb.com/try/download/community2

# Notes on how to implement mongodb in python script:
## Atlas connection string:
    mongodb+srv://Reech:amazingDev!1@reechdb.ojmoq.mongodb.net/?retryWrites=true&w=majority
## Run python file
    python matching_engine/launch.py
## Initialise mongoDB client object
    client = pymongo.MongoClient("mongodb+srv://Reech:amazingDev!1@reechdb.ojmoq.mongodb.net/?retryWrites=true&w=majority")

# Useful packages, to be looked into later:
Improving/implementing scheduling: celery python





