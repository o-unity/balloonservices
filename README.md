# balloonservices

## info
    http://blog.miguelgrinberg.com/post/easy-websockets-with-flask-and-gevent

## Prerequisits for socketserver (2.7)
    pip install flask-socketio
    pip install coverage
    pip install eventlet


## Prerequisits for client (3.5)


## Testcoverage
    coverage erase
    coverage run --branch --source=. --omit=test/*,*.cfg test/resttest.py
    coverage xml -i
    coverage report -m
    coverage html
