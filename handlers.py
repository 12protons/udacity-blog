import blog
import models
from google.appengine.ext import db
import logging

class SignupHandler(blog.BlogHandler):
    def render_signup(self, username="", email="", error=""):
        self.render("signup.html", username=username, email=email, error=error)

    def get(self):
        self.render_signup()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        error = ""

        if not username or not password or not verify or password != verify:
            error = "Form Error!"

        existing_user = db.GqlQuery("SELECT * FROM User WHERE username = :1", username).count()
        if existing_user:
            error = "User Exists!"

        if not error:
            password_hash = self.make_pw_hash(name=username, pw=password)

            user = models.User(username=username,password_hash=password_hash,email=email)
            user.put()

            user_id = str(user.key().id())
            self.write_cookie('name', user_id)

            self.redirect("/blog/welcome")

        else:
            self.render_signup(username=username, email=email, error=error)

class WelcomeHandler(blog.BlogHandler):
    def render_welcome(self, username):
        self.render("welcome.html", username=username)

    def get(self):
        user_id = self.read_cookie('name')
        if user_id:
            username = models.User.get_by_id(int(user_id)).username
        if username:
            self.render_welcome(username=username)
        else:
            self.redirect("/blog/signup")

class LoginHandler(blog.BlogHandler):
    def render_login(self, error=""):
        self.render("login.html", error=error)

    def get(self):
        self.render_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        existing_user = db.GqlQuery("SELECT * FROM User WHERE username = :1", username)[0]

        if not existing_user:
            self.render_login(error="No such user exists!")

        if not self.validate_pw(name=username, pw=password, h=existing_user.password_hash):
            self.render_login(error="Invalid password!")

        user_id = str(existing_user.key().id())
        self.write_cookie('name', user_id)

        self.redirect("/blog/welcome")

class LogoutHandler(blog.BlogHandler):
    def get(self):
        self.write_cookie("name", "")
        self.redirect("/blog/signup")

class NewPostHandler(blog.BlogHandler):
    def render_newblog(self, subject="", content="", error=""):
        self.render("newpost.html", subject=subject, content=content, error=error)

    def get(self):
        self.redirect_if_not_logged_in()
        self.render_newblog()

    def post(self):
        self.redirect_if_not_logged_in()

        subject = self.request.get("subject")
        content = self.request.get("content")
        author_id = self.logged_in()

        if subject and content:
            a = models.Post(subject = subject, content = content, author = author_id)
            a.put()

            post_id = a.key().id()

            self.redirect("/blog/%s" % post_id)
        else:
            error = "need both subject and content!"
            self.render_newblog(subject=subject, content=content, error=error)

class PostHandler(blog.BlogHandler):
    def render_post(self, subject="", content="", authorname=""):
        self.render("post.html", subject=subject, content=content, authorname=authorname)

    def get(self, post_id):
        post = models.Post.get_by_id(int(post_id))
        subject = post.subject
        content = post.content
        
        author_id = post.author
        author = models.User.get_by_id(int(author_id))

        self.render_post(subject=subject, content=content, authorname=author.username)

class HomeHandler(blog.BlogHandler):
    def render_blog(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render("blog.html", posts=posts)

    def get(self):
        self.render_blog()