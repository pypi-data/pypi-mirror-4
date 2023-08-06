""" Initialize web application package """

from os import path
import bottle

BASE_PATH = '/test' # application base, proxy forwards anything starting with this

app = bottle.Bottle() #create app

@app.route('/') # http://localhost:8080/
@app.route('/where') # http://localhost:8080/where
def testGet():
    """ Test endpoint"""
    bottle.response.set_header('content-type', 'text/plain')
    content =  "Web app is located at %s" % path.dirname(path.abspath(__file__))
    return content

# import ends before files so ends routes take precedence
import ends # dynamic rest endpoint package   
import files #static file package

tmpapp = bottle.default_app()
tmpapp.mount(BASE_PATH, app) #remount app to be behind BASE_PATH for proxy
app = tmpapp #now make app point to remounted app
# http://localhost:8080/test
# http://localhost:8080/test/where