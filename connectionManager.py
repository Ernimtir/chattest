#!/usr/bin/env python

from esUtils import *
from esModels import *
from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.ext.webapp.util import run_wsgi_app	

# With DCHandler, manages client connection awareness
class CHandler(webapp.RequestHandler):
	def get(self):
		return
		
	def post(self):
		client_id = self.request.get('from')
		client = client_id.split(None,1)
		room = client[0]
		nickname = client[1]
		user = get_user()
		user.room = room;
		user.put()
		content = dict()
		content['name'] = nickname
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			channel.send_message(room+" "+player.user.user_id(), 
				buildJSONMessage('connect', content))

# With CHandler, manages client connection awareness
class DCHandler(webapp.RequestHandler):

	def get(self):
		return # f right off

	def post(self):
		client_id = self.request.get('from')
		client = client_id.split(None,1)
		room = client[0]
		nickname = client[1]
		user = get_user()
		user.room = '';
		user.put()
		content = dict()
		content['name'] = nickname
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			channel.send_message(room+" "+player.user.user_id(), 
				buildJSONMessage('disconnect', content))
				
				
class RCHandler(webapp.RequestHandler):
	def get(self):
		return
		
	def post(self):
		room = self.request.get('msg')
		token = channel.create_channel(room+get_user().user.user_id())
		content = dict()
		content['token'] = token
		self.response.out.write(buildJSONMessage('reconnect', content))
		
def main():
    app = webapp.WSGIApplication(
		[
			(r'/_ah/channel/connected/', CHandler),
			(r'/_ah/channel/disconnected/', DCHandler),
			(r'/tokenrequest', RCHandler),
		],
        debug=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
