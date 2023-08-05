from twisted.web.resource import Resource
from urlparse import urlparse, parse_qs
from Controllers.datahandler import DataHandler
from Networking.statuscodes import StatusCodes

class TwistedHandler(Resource):

    networking = None

    isLeaf = True

    def __init__(self, networking):
        self.networking = networking
        self.datahandler = DataHandler()
        Resource.__init__(self)

    def render_GET(self, request):

        key = None

        if "apitoken" in request.args:
            key = request.args['apitoken']

        response = self.datahandler.handleIt(0, request.path, key, None)

        request.setResponseCode(response.code)
        return response.json

    def render_POST(self, request):
        
        try:
            data = request.args['data'][0]
        except:
            data = ""

        key = None

        if "apitoken" in request.args:
            key = request.args['apitoken']

        response = self.datahandler.handleIt(1, request.path, key, data)

        request.setResponseCode(response.code)
        return response.json

    def render_PUT(self, request):

        try:
            data = request.args['data'][0]
        except:
            data = ""

        key = None

        if "apitoken" in request.args:
            key = request.args['apitoken']

        response = self.datahandler.handleIt(2, request.path, key, data)

        request.setResponseCode(response.code)
        return response.json

    def render_DELETE(self, request):
        key = None

        if "apitoken" in request.args:
            key = request.args['apitoken']

        response = self.datahandler.handleIt(3, request.path, key, None)

        request.setResponseCode(response.code)
        return response.json