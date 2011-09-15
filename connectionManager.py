#!/usr/bin/env python

from esUtils import *
from esModels import *
from django.utils import simplejson as json
from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.ext.webapp.util import run_wsgi_app	

# With DCHandler, manages client connection awareness
class CHandler(webapp.RequestHandler):
	def get(self):
		return
		
	def post(self):
		client_id = self.request.get('from')
		logging.info(client_id)
		client = client_id.split(None,1)
		room = client[0]
		user = db.get(db.Key.from_path('Player', client[1])) # Key object from client ID used to locate corresponding datastore entry
		
		content = dict()
		content['name'] = user.user.nickname()
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			logging.info(player.user.user_id())
			channel.send_message(" ".join([room, player.user.user_id()]), 
				buildJSONMessage('connect', content))
		user.room = room;
		logging.info(room)
		user.put()

# With CHandler, manages client connection awareness
class DCHandler(webapp.RequestHandler):
	def get(self):
		return # f right off

	def post(self):
		client_id = self.request.get('from')
		client = client_id.split(None,1)
		logging.info(client_id)
		room = client[0]
		user = db.get(db.Key.from_path('Player', client[1]))
		# user.room = '';
		user.put()
		content = dict()
		content['name'] = user.user.nickname()
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			channel.send_message(" ".join([room, player.user.user_id()]), 
				buildJSONMessage('disconnect', content))
				
class TokenHandler(webapp.RequestHandler):
	def get(self):
		return
		
	def post(self):
		msgJSON = self.request.get('json')
		logging.info(str(msgJSON))
		msgobj = json.JSONDecoder().decode(msgJSON)
		if (msgobj["type"] != "system"): return
		room = msgobj["content"]["room"]
		user = get_user()
		user.room = room
		user.put()
		token = channel.create_channel(" ".join([room, user.user.user_id()]))
		content = dict()
		content['token'] = token
		logging.info(token)
		self.response.out.write(buildJSONMessage('connect', content))
		
def main():
    app = webapp.WSGIApplication(
		[
			(r'/_ah/channel/connected/', CHandler),
			(r'/_ah/channel/disconnected/', DCHandler),
			(r'/tokenrequest', TokenHandler)
		],
        debug=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
