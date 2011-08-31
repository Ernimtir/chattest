#!/usr/bin/env python

from google.appengine.ext import db

class Player(db.Model):
	user = db.UserProperty(auto_current_user_add=True)
	nick = db.StringProperty()
	room = db.StringProperty()
	token = db.StringProperty()
	avail = db.BooleanProperty()

class ChatEntry(db.Model):
	msg = db.TextProperty()
	form = db.StringProperty()
	nick = db.StringProperty()
	room = db.StringProperty()
	time = db.DateTimeProperty(auto_now_add=True)
	user = db.UserProperty(auto_current_user_add=True)
