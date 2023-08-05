import BaseHTTPServer
import os
import shutil
import mimetypes
from omdox import settings
from omdox import render
from omdox import feedback
HOST_NAME = 'localhost' 
PORT_NUMBER = 7000


SRC = os.getcwd()
BUILD = os.path.join(SRC, '_build')

def chunked_read(file_obj, size=1024):
    while True:
        data = file_obj.read(size)
        if not data:
            break
        yield data

def serve404(s):
    s.send_response(404)
    s.send_header("Content-type", "text/html")
    s.end_headers()
    s.wfile.write("<html><head><title>?</title></head>")
    s.wfile.write("<body><p>404</p></body></html>")
    return

class DocHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        return

    def do_GET(s):
        #
        #
        #
        # make the source and build paths
        src_obj = '%s%s' % (SRC, s.path)
        build_obj = '%s%s' % (BUILD, s.path)
        ext = os.path.splitext(src_obj)[-1]
        #
        #
        #
        # if the file does not exist 404 
        if not os.path.exists(src_obj):
            return serve404(s)
        #
        #
        #
        # it exists so get the mimetype
        try:
            content_type = mimetypes.guess_type(src_obj)[0]
        except IndexError:
            content_type  = 'application/octet-stream'
        #
        #
        #
        #
        # is it a directory?
        if os.path.isdir(src_obj):
            # is index.html present in it?
            if os.path.exists(os.path.join(src_obj, 'index.html')):
               # redefine what we're looking for
               src_obj = os.path.join(src_obj, 'index.html')
               build_obj = os.path.join(build_obj, 'index.html')
               ext = '.html'
        #
        #
        #
        # process and get the hell out of dodge
        #
        #
        # ignores
        if src_obj in settings.EXCLUDED:
            return serve404
        # now build the nodes
        if src_obj in settings.UTILITY_NODES:
            return serve404
        elif ext in settings.EXTENTIONS:
            render.render(src_obj, build_obj)
            if ext == '.html':
                feedback.info('[serve] %s' % s.path)
        else:
            shutil.copyfile(src_obj, build_obj)
        #
        #
        # send headers
        s.send_response(200)
        s.send_header('Content-type', content_type)
        s.end_headers()
        #
        #
        # read the file into the response
        response = ''
        #
        f = open(build_obj)
        for chunk in chunked_read(f):
            response += chunk
        f.close()
        # send response
        s.wfile.write(response)





"""import os
from bottle import route, static_file


cwd = os.getcwd()

@route('<filename:path>')
def index(filename):
    # if filename end in a slash then change it to index.html
    obj = '%s/_build/%s' % (cwd, filename)
    if os.path.isdir(obj):
        filename = '%s/index.html' % filename
    # if the file is html, return that as a response
    if filename.split('.').pop() == 'html':
        htmlfile = open('%s/_build/%s' % (cwd, filename), 'r')
        html = htmlfile.read()
        htmlfile.close()
        return html
    return static_file(filename, root='%s/_build' % cwd)
"""
