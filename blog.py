import os
import webapp2
import jinja2
import random
import string
import hmac

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

# Crypto
SECRET = 'imsosecret'
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Base Handler
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        kw['user_is_logged_in'] = self.logged_in()
        self.write(self.render_str(template, **kw))

    def write_cookie(self, cookie_name, cookie_value):
        cookie_value = make_secure_val(cookie_value)
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (cookie_name, cookie_value))

    def read_cookie(self, cookie_name):
        cookie_secure_value = self.request.cookies.get(cookie_name)
        cookie_value = ""

        if cookie_secure_value:
            cookie_value = check_secure_val(cookie_secure_value)

        return cookie_value

    def make_pw_hash(self, name, pw, salt = None):
        if not salt:
            salt = make_salt()
        h = hash_str(name + pw + salt)
        return '%s,%s' % (h, salt)

    def validate_pw(self, name, pw, h):
        salt = h.split(',')[1]
        return h == self.make_pw_hash(name, pw, salt)

    def logged_in(self):
        return self.read_cookie('name')

    def redirect_if_not_logged_in(self):
        if not self.logged_in():
            self.redirect('/blog/signup')