#!/usr/bin/env python

import os
import re
import logging
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.dist import use_library
use_library('django', '1.2')
from google.appengine.ext.webapp import template

def render(template_file, template_values):
	logging.info(os.path.join(os.path.dirname(__file__), 'templates', template_file))
	return template.render(				# render a template
		os.path.join(					# system specific path joiner
			os.path.dirname(__file__),	# path to this python file
			'templates',				# enter templates directory
			template_file),				# template file
		template_values)				# values to pass to renderer

class Player(db.Model):
#	user = db.UserProperty(auto_current_user_add=True)
	nick = db.StringProperty()
	
def get_user():
	# returns the current user's site_user entity from the datastore
	# or creates it if one doesn't exist yet
	user = users.get_current_user()
	if user:
		# user is logged in
		user_id = user.user_id()
		if user_id is not None:
			# user has a unique permanent ID
			player = db.get(db.Key.from_path('Player', user_id))
			if player is None:
				# player entity hasn't been created yet
				player = Player(key_name=user_id)
				player.nick = user.nickname()
				player.put()
			return player
		else:
			# user DOES NOT have a unique permanent ID
			logging.info(''.join['user lacks permanent ID: ',user.nickname()])
			return False
	else:
		# user not logged in
		return False

class ChatEntry(db.Model):
	text = db.StringProperty()
	timestamp = db.DateTimeProperty(auto_now_add=True)
#	author = db.ReferenceProperty(reference_class=Player, collection_name="postings")
#	author = db.StringProperty()
	room = db.StringProperty()

class MainHandler(webapp.RequestHandler):
    def get(self, room):
		template_values = {}
		
		chatq = ChatEntry.all()
		chatq.filter("room =", room)
		chatq.order("timestamp")
		chatlog = '\n'.join([entry.text for entry in chatq])
		
		template_values['room'] = room
		template_values['chatlog'] = chatlog
		
		self.response.out.write(render('chat.html', template_values))
        
    def post(self, room):
		entry = ChatEntry()
		entry.text = self.request.get("message")
		if entry.text:
			m = re.match(r'^/(.*?)\s+(.+)', entry.text)
			if m:
				if m.group(1) == 'nick':
					user = get_user()
					user.nick = m.group(2)
					user.put()
					self.redirect('/'+room)
					return
				elif m.group(1) == 'ooc':
					entry.text = ''.join([get_user().nick, ': (( ', m.group(2), ' ))'])
				elif m.group(1) == 'me' or 'em':
					entry.text = ' '.join([get_user().nick, m.group(2)])
			else:
				entry.text = ''.join([get_user().nick, ': ', entry.text])
			entry.room = room
			entry.put()
		self.redirect('/'+room)

def main():
    app = webapp.WSGIApplication(
		[
			(r'/(.*)', MainHandler)
		],
        debug=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
