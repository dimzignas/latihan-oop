#!/usr/bin/env python
# coding: utf-8

# In[2]:


import requests
r = requests.get('http://itb.ac.id')
print(r.status_code)
print(r.headers)
print(r.content)


# In[4]:


import requests
r = requests.get('http://localhost:8080')
print(r.status_code)
print(r.headers)
print(r.content)


# In[5]:


import http.server
import socketserver

PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()


# In[5]:


import http.server
import socketserver

PORT = 8081
Handler = http.server.SimpleHTTPRequestHandler
Handler.directory = './other-directory/'

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(Handler.directory)
    print("serving at port", PORT)
    httpd.serve_forever()


# In[8]:


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import parse_qs
import cgi

class GP(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_HEAD(self):
        self._set_headers()
    def do_GET(self):
        self._set_headers()
        print(self.path)
        print(parse_qs(self.path[2:]))
        self.wfile.write("<html><body><h1>Get Request Received!</h1></body></html>")
    def do_POST(self):
        self._set_headers()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        print(form.getvalue("foo"))
        print(form.getvalue("bin"))
        self.wfile.write("<html><body><h1>POST Request Received!</h1></body></html>")

def run(server_class=HTTPServer, handler_class=GP, port=8088):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Server running at localhost:8088...')
    httpd.serve_forever()

run()


# In[ ]:




