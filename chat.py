#!/usr/bin/env python

import re
import random
import logging
from esUtils import *
from esModels import *
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import channel
from django.utils import simplejson as json
from google.appengine.ext.webapp.util import run_wsgi_app	

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

		chanID = " ".join([room, get_user().user_id])
		logging.info(chanID)
		token = channel.create_channel(chanID)

		template_values['room'] = room
		template_values['chatlog'] = chatlog

		self.response.out.write(render('chat.html', template_values))


    def post(self, room):
		message = self.request.get('json')
		user = get_user()
		
		decoder = json.JSONDecoder()
		encoder = json.JSONEncoder()
		
		msgJSON = decoder.decode(message)
		response = ''
		content = dict()
		if msgJSON['type'] == "chat":
			if user.style:
				style = decoder.decode(user.style)
			entry = ChatEntry()
			
			entry.text = msgJSON['content']['text'] #pull message
			entry.text = re.sub(r'\[(\d+)d(\.dmg)?\]', ExRoller, entry.text)
			entry.text = re.sub(r'\[(\d+)d(\d+)t?\]', NRoller, entry.text)
			
			stylestring = ""
#			for k,v in style:
#				stylestring = stylestring+k+":"+v+";"
			
			if entry.text[0] == '/':
				msg = entry.text.split(None,1)
				entry.text = msg[1]
				if msg[0]:
					command = msg[0].lstrip('/')
					if command == 'nick':
						oldnick = user.nick
						user.nick = entry.text
						entry.text = oldnick+' is now known as '+entry.text+'.'
						user.put()
					elif command == 'asem' or command == "asme":
						entry.text = '*'+entry.text+'*'
					elif command == 'as':
						msg = entry.text.split(None,1)
						entry.text = msg[0]+": "+msg[1]
					elif command == 'coinflip' or command =='cf':
						if (random.randint(0,1)):
							result = heads
						else: 
							result = tails
						entry.text = '*'+'<span style="'+stylestring+'"> '+user.nick+" flipped "+result+".</span>"
					elif command == 'ooc':
						entry.text = user.user.nickname()+': (( '+entry.text+' ))'
					elif command == 'color':
						if (str.len(entry.text) == 6 or str.len(entry.text) == 3) and isHex(entry.text):
							style['color'] = entry.text
							user.style = encoder.encode(style)
							user.put()
							content['text'] = 'Color changed to: '+entry.text
							channel.send_message(" ".join([room, user.user_id]), # Uses Key object so each channel also references user
								buildJSONMessage('alert', content))
							return
						else:
							content['text'] = "Invalid color code: "+entry.text
							channel.send_message(" ".join([room, user.user_id]), # Uses Key object so each channel also references user
								buildJSONMessage("alert", content))
							return
					elif command == 'me' or 'em':
						entry.text = '*<span style="'+stylestring+'">'+user.nick+entry.text+"</span>"
					else:
						content['text'] = "Bad command in: "+entry.text
						channel.send_message(" ".join([room, user.user_id]), # Uses Key object so each channel also references user
							buildJSONMessage("alert", content))
						return
				
			else:
				entry.text = ''.join(['<span style="',stylestring,'">',user.nick,": ",entry.text,'</span>'])
			entry.room = room
			content["text"] = entry.text
			response = buildJSONMessage("chat", content)
			entry.put()
			user.put()
		elif msgJSON['type'] == "system":
			pass # nothing here yet
		else:
			return # Bad data
		roomquery = Player.all()
		roomquery.filter('room =', room)
		for player in roomquery:
			channel.send_message(" ".join([room, str(player.key())]), response);  # Uses Key object so each channel also references player

def main():
    app = webapp.WSGIApplication(
		[
			(r'/chat/(.*)', MainHandler)
		],
        debug=True)
    run_wsgi_app(app)


if __name__ == '__main__':
    main()
