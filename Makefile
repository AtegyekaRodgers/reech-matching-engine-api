install:  
    @echo Make sure you are running in a virtual env!!
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    python3 -m pip install -e matching_engine

# runs the API
api:
    python3 -m uvicorn matching_engine.app.main:app 

