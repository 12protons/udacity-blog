from google.appengine.ext import db

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    author = db.StringProperty(required = True)
    liked_by_users = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

class User(db.Model):
    username = db.StringProperty(required = True)
    password_hash = db.StringProperty(required = True)
    email = db.StringProperty()

class Comment(db.Model):
    user_id = db.StringProperty(required = True)
    post_id = db.StringProperty(required = True)
    content = db.StringProperty(required = True)