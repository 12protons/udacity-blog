import handlers
import models
import webapp2
from google.appengine.ext import db

app = webapp2.WSGIApplication([
    ('/blog', handlers.HomeHandler),
    ('/blog/newpost', handlers.NewPostHandler),
    ('/blog/(\d+)', handlers.PostHandler),
    ('/blog/signup', handlers.SignupHandler),
    ('/blog/welcome', handlers.WelcomeHandler),
    ('/blog/logout', handlers.LogoutHandler),
    ('/blog/login', handlers.LoginHandler)
], debug=True)
