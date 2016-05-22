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
    ('/blog/login', handlers.LoginHandler),
    ('/blog/edit/(\d+)', handlers.EditPostHandler),
    ('/blog/delete/(\d+)', handlers.DeletePostHandler),
    ('/blog/like/(\d+)', handlers.LikePostHandler),
    ('/blog/(\d+)/editcomment/(\d+)', handlers.EditCommentHandler),
    ('/blog/(\d+)/deletecomment/(\d+)', handlers.DeleteCommentHandler)
], debug=True)
