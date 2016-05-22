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

        existing_user = db.GqlQuery(
            "SELECT * FROM User WHERE username = :1", username).count()
        if existing_user:
            error = "User Exists!"

        if not error:
            password_hash = self.make_pw_hash(name=username, pw=password)

            user = models.User(
                username=username, password_hash=password_hash, email=email)
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
        redirected = self.redirect_if_not_logged_in()
        if redirected:
            return

        user_id = self.read_cookie('name')
        username = models.User.get_by_id(int(user_id)).username
        self.render_welcome(username=username)


class LoginHandler(blog.BlogHandler):
    def render_login(self, error=""):
        self.render("login.html", error=error)

    def get(self):
        self.render_login()

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        existing_users = db.GqlQuery(
            "SELECT * FROM User WHERE username = :1", username)

        if existing_users.count(1) == 0:
            self.render_login(error="No such user exists!")
            return

        existing_user = existing_users[0]

        if not self.validate_pw(name=username,
                                pw=password,
                                h=existing_user.password_hash):
            self.render_login(error="Invalid password!")
            return

        user_id = str(existing_user.key().id())
        self.write_cookie("name", user_id)

        self.redirect("/blog/welcome")


class LogoutHandler(blog.BlogHandler):
    def get(self):
        self.write_cookie("name", "")
        self.redirect("/blog/login")


class NewPostHandler(blog.BlogHandler):
    def render_newblog(self, subject="", content="", error=""):
        self.render(
            "newpost.html", subject=subject, content=content, error=error)

    def get(self):
        redirected = self.redirect_if_not_logged_in()
        if redirected:
            return

        self.render_newblog()

    def post(self):
        redirected = self.redirect_if_not_logged_in()
        if redirected:
            return

        subject = self.request.get("subject")
        content = self.request.get("content")
        author_id = self.logged_in()

        if subject and content:
            a = models.Post(subject=subject,
                            content=content,
                            author=author_id,
                            liked_by_users="")
            a.put()

            post_id = a.key().id()

            self.redirect("/blog/%s" % post_id)
        else:
            error = "need both subject and content!"
            self.render_newblog(subject=subject, content=content, error=error)


class PostHandler(blog.BlogHandler):
    def render_post(self,
                    post_id,
                    subject,
                    content,
                    authorname,
                    comments,
                    error=""):

        self.render("post.html",
                    post_id=post_id,
                    subject=subject,
                    content=content,
                    authorname=authorname,
                    comments=comments,
                    error=error)

    def get(self, post_id):
        post = models.Post.get_by_id(int(post_id))
        subject = post.subject
        content = post.content

        author_id = post.author
        author = models.User.get_by_id(int(author_id))

        comments = db.GqlQuery(
            "SELECT * FROM Comment WHERE post_id = :1", post_id)

        self.render_post(post_id=post_id, subject=subject,
                         content=content, comments=comments,
                         authorname=author.username)

    def post(self, post_id):
        redirected = self.redirect_if_not_logged_in()
        if redirected:
            return

        user_id = self.logged_in()
        comment_content = self.request.get("comment")
        if comment_content:
            comment = models.Comment(user_id=user_id, post_id=post_id,
                                     content=comment_content)
            comment.put()
            self.redirect("/blog/%s" % post_id)
        else:
            error = "You cant submit empty comments!"

            post = models.Post.get_by_id(int(post_id))
            subject = post.subject
            content = post.content

            author_id = post.author
            author = models.User.get_by_id(int(author_id))

            self.render_post(subject=subject, content=content,
                             authorname=author.username, error=error)


class HomeHandler(blog.BlogHandler):
    def render_blog(self, posts):
        self.render("blog.html", posts=posts)

    def get(self):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
        self.render_blog(posts)


class EditPostHandler(blog.BlogHandler):
    def render_edit(self, post_id, subject, content, error=""):
        self.render("editpost.html", post_id=post_id, subject=subject,
                    content=content, error=error)

    def get(self, post_id):
        redirected = self.redirect_if_not_logged_in()
        redirected &= self.redirect_if_not_owned(post_id)
        if redirected:
            return

        post = models.Post.get_by_id(int(post_id))
        subject = post.subject
        content = post.content

        self.render_edit(post_id=post_id, subject=subject, content=content)

    def post(self, post_id):
        redirected = self.redirect_if_not_logged_in()
        redirected &= self.redirect_if_not_owned(post_id)
        if redirected:
            return

        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            post = models.Post.get_by_id(int(post_id))
            post.subject = subject
            post.content = content
            post.put()

            self.redirect("/blog/%s" % post_id)
        else:
            error = "need both subject and content!"
            self.render_edit(post_id=post_id, subject=subject,
                             content=content, error=error)


class DeletePostHandler(blog.BlogHandler):
    def get(self, post_id):
        redirected = self.redirect_if_not_logged_in()
        redirected &= self.redirect_if_not_owned(post_id)
        if redirected:
            return

        post = models.Post.get_by_id(int(post_id))
        db.delete(post)
        self.redirect("/blog")


class LikePostHandler(blog.BlogHandler):
    def get(self, post_id):
        redirected = self.redirect_if_not_logged_in()
        if redirected:
            return

        user_id = str(self.logged_in())
        post = models.Post.get_by_id(int(post_id))
        if post.author != user_id and user_id not in post.liked_by_users:
            post.liked_by_users += "|" + user_id
            post.put()

        self.redirect("/blog")


class EditCommentHandler(blog.BlogHandler):
    def render_edit(self, post_id, comment_id, content, error=""):
        self.render("editcomment.html", post_id=post_id,
                    comment_id=comment_id, content=content, error=error)

    def get(self, post_id, comment_id):
        redirected = self.redirect_if_not_logged_in()
        redirected &= self.redirect_if_comment_not_owned(post_id, comment_id)
        if redirected:
            return

        comment = models.Comment.get_by_id(int(comment_id))
        self.render_edit(post_id, comment_id, comment.content)

    def post(self, post_id, comment_id):
        redirected = self.redirect_if_not_logged_in()
        redirected &= self.redirect_if_comment_not_owned(post_id, comment_id)
        if redirected:
            return

        content = self.request.get("content")

        if content:
            comment = models.Comment.get_by_id(int(comment_id))
            comment.content = content
            comment.put()
            self.redirect("/blog/%s" % post_id)
        else:
            error = "You cant have empty comments!"
            self.render_edit(post_id, comment_id, comment.content)


class DeleteCommentHandler(blog.BlogHandler):
    def get(self, post_id, comment_id):
        redirected = self.redirect_if_not_logged_in()
        redirected &= self.redirect_if_comment_not_owned(post_id, comment_id)
        if redirected:
            return

        comment = models.Comment.get_by_id(int(comment_id))
        db.delete(comment)
        self.redirect("/blog/%s" % post_id)
