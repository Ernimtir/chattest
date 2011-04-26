#!/usr/bin/env python

import os
import re
import random
import logging
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.api import channel
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

def render(template_file, template_values):
	return template.render(				# render a template
		os.path.join(					# system specific path joiner
			os.path.dirname(__file__),	# path to this python file
			'templates',				# enter templates directory
			template_file),				# template file
		template_values)				# values to pass to renderer

class Player(db.Model):
	user = db.UserProperty(auto_current_user_add=True)
	nick = db.StringProperty()
	room = db.StringProperty()
	token = db.StringProperty()

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
	text = db.TextProperty()
	timestamp = db.DateTimeProperty(auto_now_add=True)
	room = db.StringProperty()
	
def roller(matchobj):
	num_dice = int(matchobj.group(1))
	rolls = []
	successes = 0
	botch = False
	for die in xrange(0, num_dice):
		rolls.append(random.randint(1,10))
		if rolls[die] >= 7:
			successes += 1
			if rolls[die] == 10 and matchobj.group(2) != '.dmg':
				successes += 1
		elif rolls[die] == 1:
			botch = True
	rolls.sort()
	rolls = ', '.join(str(roll) for roll in rolls)
	if botch and successes == 0:
		result = 'BOTCH! )'
	elif successes == 1:
		result = '1 success )'
	else:
		result = str(successes) + ' successes )'
	return ''.join([
			'([',
			rolls,
			'] = ',
			result
		 ])
	
class MainHandler(webapp.RequestHandler):
    def get(self, room):
		if room == 'favicon.ico':
			# requests to this uri were logging players into
			# the 'favicon.ico' room, so abort on that case
			return
		user = get_user()
		user.room = room;
		user.put()
		
		template_values = {}

		chatquery = ChatEntry.all()
		chatquery.filter('room =', room)
		chatquery.order('timestamp')
		chatlog = '\n'.join([entry.text for entry in chatquery])

		token = channel.create_channel(room + users.get_current_user().user_id())

		template_values['room'] = room
		template_values['chatlog'] = chatlog		
		template_values['token'] = token

		self.response.out.write(render('chat.html', template_values))

    def post(self, room):
		entry = ChatEntry()
		entry.text = self.request.get('msg')
		entry.text = re.sub(r'\[(\d+)d(\.dmg)?\]', roller, entry.text)
		if entry.text:
			m = re.match(r'^/(.*?)\s+(.+)', entry.text)
			if m:
				if m.group(1) == 'nick':
					user = get_user()
					user.nick = m.group(2)
					user.put()
					return
				elif m.group(1) == 'ooc':
					entry.text = ''.join([get_user().user.nickname(), ': (( ', m.group(2), ' ))'])
				elif m.group(1) == 'me' or 'em':
					entry.text = ' '.join([get_user().nick, m.group(2)])
			else:
				entry.text = ''.join([get_user().nick, ': ', entry.text])
			entry.room = room
			entry.put()
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			channel.send_message(room + player.user.user_id(), entry.text);

def main():
    app = webapp.WSGIApplication(
		[
			(r'/(.*)', MainHandler)
		],
        debug=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
