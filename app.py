from app import app
port = 2000  # the custom port you want
app.run(host='0.0.0.0', port=port,debug=True)

# from app import app
# from gevent.pywsgi import WSGIServer
# from gevent import pywsgi
# port = 3333  # the custom port you want
# host='0.0.0.0'
# app.run(host, port=port,debug=True)
# http_server = WSGIServer((host, port), app)
# http_server.serve_forever()
# if __name__ == "__main__":
#     app.run(debug=True)


