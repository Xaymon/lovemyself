
from app import app
from gevent.pywsgi import WSGIServer
from gevent import pywsgi
port = 5000  # the custom port you want
host='0.0.0.0'
app.run(host, port=port,debug=True)
# http_server = WSGIServer((host, port), app)
# http_server.serve_forever()
if __name__ == "__main__":
    app.run(debug=True)
