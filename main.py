#!/usr/bin/env python

import os
import re
import random
import logging
import time
import hashlib
from django.utils import simplejson as json
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
	style = db.StringProperty()
	

def get_user():
	# returns the current user's site_user entity from the datastore
	# or creates it if one doesn't exist yet
	user = users.get_current_user()
	if user:
		# user is logged in
		user_id = user.user_id()
		if user_id:
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

def isHex(checkstring):
	for a in checkstring:
		if string.hexdigits.find(a) <0:
			return false
	return true

def NRoller(matchobj):
	num_dice = int(matchobj.group(1))
	die_size = int(matchobj.group(2))
	rolls = []
	for die in xrange(0, num_dice):
		rolls.append(random.randint(1,die_size))
		total += rolls[die]
	rolls.sort()
	rolls = ', '.join(str(roll) for roll in rolls)
	start = "("+num_dice+"d"+die_size+": ("
	if matchobj.group(3) == 't':
		end = "] Total = " + total + ")"
	else:
		end = "])"
	return ''.join([
			start,
			rolls,
			end
		])
		
# content is a dictionary
def buildJSONMessage(type, content):
	builtcontent = dict()
	builtcontent['type'] = type
	builtcontent['content'] = content
	message = json.JSONEncoder().encode(builtcontent) # It's that easy!
	return message

def ExRoller(matchobj):
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
			channel.send_message(room +" "+player.user.nickname(), 
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
			channel.send_message(room +" "+player.user.nickname(), 
				buildJSONMessage('disconnect', content))
		

class MainHandler(webapp.RequestHandler):
    def get(self, room):
		if room == 'favicon.ico':
			# requests to this uri were logging players into
			# the 'favicon.ico' room, so abort on that case
			return

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

		
		message = self.request.get('msg')
		user = get_user()
		
		decoder = json.JSONDecoder()
		encoder = json.JSONEncoder()
		
		msgJSON = decoder(message)
		response = ''
		content = dict()
		if msgJSON[type] == "chat":
			style = decoder.decode(user.style)
			entry = ChatEntry()
			
			entry.text = msgJSON[content][text] #pull message
			entry.text = re.sub(r'\[(\d+)d(\.dmg)?\]', ExRoller, entry.text)
			entry.text = re.sub(r'\[(\d+)d(\d+)t?\]', NRoller, entry.text)
			
			stylestring = "{"
						for k,v in style.items():
							stylestring = stylestring+": "+v+"; "
						stylestring = stylestring + "}"
			
			if entry.text[0] == '/':
				msg = entry.text.split(None,1)
				entry.text = msg[1]
				if msg[0]:
					command = string.lstrip(msg[0],'/')
					if command == 'nick':
						user.nick = entry.text
						content["alert"] = 'Nick changed to: '+entry.text+'.'
						channel.send_message(room + user.user_id(), 
								buildJSONMessage("system",content))
						user.put()
						return
					elif command == 'asem' or command == "asme":
						entry.text = '*'+entry.text
					elif command == 'as':
						msg = entry.text.split(None,1)
						entry.text = msg[0]+": "+msg[1]
					elif command == 'coinflip' or command =='cf':
						if (random.randint(0,1)):
							result = heads
						else: 
							result = tails
						entry.text = '*'+'<span style="'+stylestring+'"> '+get_user().nick+" flipped "+result+".</span>"
					elif command == 'ooc':
						entry.text = get_user().user.nickname()+': (( '+entry.text+' ))'
					elif command == 'color':
						if (str.len(entry.text) == 6 or str.len(entry.text) == 3) and isHex(entry.text):
							style[color] = entry.text
							user.style = encoder.encode(style)
							content["alert"] = 'Color changed to: '+entry.text
							channel.send_message(room + user.user_id(), 
								buildJSONMessage("system", content))
							return
						else:
						content["alert"] = "Invalid color code: "+entry.text
							channel.send_message(room + user.user_id(), 
								buildJSONMessage("system", content))
							return
					elif command == 'me' or 'em':
						entry.text = '*<span style="'+stylestring+'"> '+get_user().nick+entry.text+"</span>"
					else:
					content["alert"] = "Bad command in: "+entry.text
						channel.send_message(room + user.user_id(), 
							buildJSONMessage("system", content))
						return
				
			else:
				entry.text = entry.text.join(['<span style="',stylestring,'"> ',get_user.nick,": ",entry.text])
			entry.room = room
			content["text"] = entry.text
			response = buildJSONMessage("chat", content)
			entry.put()
			user.put()
		elif msgJSON[type] == "system":
			# nothing here yet
		else return # Bad data
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			channel.send_message(room +" "+player.user.nickname(), response);

def main():
	users = Player.all()
	for user in users:
		user.room = ''
    app = webapp.WSGIApplication(
		[
			(r'/(.*)', MainHandler),
			(r'/_ah/channel/connected/', CHandler)
			(r'/_ah/channel/disconnected/', DCHandler)
		],
        debug=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
