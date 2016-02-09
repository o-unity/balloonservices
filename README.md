# balloonservices

## info
    http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent
    
## virtualenv
    source ballonservice/bin/activate

## Prerequisits
    pip install flask
    pip install flask-socketio
    pip install coverage
    pip install eventlet
    pip install -U socketIO-client
    pip install decorator


## Testcoverage
    coverage erase
    coverage run --branch --source=. --omit=test/*,*.cfg test/resttest.py
    coverage xml -i
    coverage report -m
    coverage html
