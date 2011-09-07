#!/usr/bin/env python

import os
import logging
from esModels import *	
from google.appengine.ext import db
from google.appengine.api import users
from django.utils import simplejson as json
from google.appengine.ext.webapp import template

def render(template_file, template_values):
	return template.render(				# render a template
		os.path.join(					# system specific path joiner
			os.path.dirname(__file__),	# path to this python file
			'templates',				# enter templates directory
			template_file),				# template file
		template_values)				# values to pass to renderer

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
		
# content parameter should be a dict, but not required
# Current message type strings: chat (chat text, displayed to all users as a convention)
#								alert (chat text, displayed to one user only as a convention)
#								system (system upkeep messages, displayed to nobody)
#								connect/disconnect (used to notify clients of other clients' status)
#								reconnect (only used in response to request for new token)
#
# No practical different exists between chat and alert style messages, the difference is
# merely to allow for easy differentiation in code

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
