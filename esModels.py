#!/usr/bin/env python

from google.appengine.ext import db

class Player(db.Model):
	user = db.UserProperty(auto_current_user_add=True)
	nick = db.StringProperty()
	room = db.StringProperty()
	style = db.StringProperty()

class ChatEntry(db.Model):
	text = db.TextProperty()
	timestamp = db.DateTimeProperty(auto_now_add=True)
	room = db.StringProperty()

