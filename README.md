# balloonservices

## info
    http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent

## Prerequisits
    pip install flask
    pip install flask-socketio
    pip install coverage
    pip install eventlet
    pip install websocket-client


## Testcoverage
    coverage erase
    coverage run --branch --source=. --omit=test/*,*.cfg test/resttest.py
    coverage xml -i
    coverage report -m
    coverage html
