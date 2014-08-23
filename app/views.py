# -*- coding: utf-8 -*-

from flask import render_template, flash, g
from jinja2 import evalcontextfilter, Markup, escape
from flask.ext.login import login_user, logout_user, login_required, current_user
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView

from forms import *
from utils import *
from models import *
import DUtils


reload(sys)
sys.setdefaultencoding('utf-8')

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
basedir = os.path.abspath(os.path.dirname(__file__))
colorlog = DUtils.ColorLog(debug=True)
secret_key = "3l4dsfalkjf30ij43jkLM"


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
                          for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


basedir = os.path.abspath(os.path.dirname(__file__))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    user = g.user
    return render_template("index.html",
                           user=user,
                           title=u'IsOnlineZilla',
    )


@app.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    user = g.user

    # ---------- list websites ---------
    records = TheModel.query.filter_by(user_email=user.user_email).all()

    return render_template("manage.html",
                           user=user,
                           records=records,
                           title='Manage my websites'
    )


@app.route('/notifications/<what>/<int:tId>', methods=['GET', 'POST'])
@login_required
def notifications(tId=0, what=""):
    user = g.user

    record = TheModel.query.filter(and_(TheModel.id == tId, TheModel.user_email == user.user_email)).first()

    if record is None:
        return "this will not work"

    if what == "disable":
        db.session.query(TheModel).filter(and_(TheModel.id == tId, TheModel.user_email == user.user_email)).update({TheModel.enable_notifications: 0})
        db.session.commit()
        flash("notification disabled", category="warning")
        return redirect(url_for("manage"))

    if what == "enable":
        db.session.query(TheModel).filter(and_(TheModel.id == tId, TheModel.user_email == user.user_email)).update({TheModel.enable_notifications: 1})
        db.session.commit()
        flash("notifications enabled", category="success")
        return redirect(url_for("manage"))


@app.route('/delete/<int:tId>', methods=['GET', 'POST'])
@login_required
def delete(tId=0):
    user = g.user

    record = TheModel.query.filter(and_(TheModel.id == tId, TheModel.user_email == user.user_email)).first()

    if record is None:
        return "this will not work"

    db.session.delete(record)
    db.session.commit()
    flash("deleted", category="warning")
    return redirect(url_for("manage"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)


    if request.method == 'POST':

        if form.validate():

            user_email = form.user_email.data
            user = Users.query.filter_by(user_email=user_email).first()

            if user is None:
                flash("no user found with this email", category="warning")
                return redirect(url_for("manage"))
            else:
                login_user(user)
                return redirect(url_for("manage"))

    return render_template("login.html",
                           form=form,
                           user=None,
                           title='Login'
    )


@app.route('/register', methods=['GET', 'POST'])
def register():

    if g.user:
        user = g.user
    else:
        user = None

    registerform = RegisterForm(request.form)

    if request.method == 'POST':

        if registerform.validate():
            user_email = registerform.user_email.data
            website = registerform.website.data
            user_ip = str(request.remote_addr)

            time.sleep(1)

            new_user = Users()
            result = new_user.add_new_user(user_email, user_ip)

            new_TheModel = TheModel()
            mResult = new_TheModel.add_new_themodel(user_email, website, user_ip)

        if mResult == "ok":
            flash("Website Added. You can now login with your email or add a new one", category="success")
            return redirect(url_for("register"))
        else:
            flash(result)
            return redirect(url_for("register"))

    return render_template("register.html",
                           user=user,
                           registerform=registerform,
                           title='Register'
    )


@login_manager.user_loader
def load_user(userid):
    return Users.get(userid)


@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out.")
    return redirect("/login")


# ------------------ SEO STUFF ------------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(401)
def not_authorized(e):
    return render_template('401.html'), 401


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("img/favicon.ico")


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("login"))


# -------------------------- ADMIN PART ------------------------------------
admin = Admin(app, name="IsOnlineZilla Admin")


class MyView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


class TheModelUnitsAdminView(ModelView):
    # Disable model creation
    can_create = True
    # Override displayed fields
    # column_list = ('id','user_email', 'category', 'notification_text', 'sent_email', 'created_date')
    def is_accessible(self):
        if request.remote_addr == '93.152.155.105':
            return True
        else:
            return False


    def __init__(self, session, **kwargs):
        super(TheModelUnitsAdminView, self).__init__(TheModel, session, **kwargs)


class UsersAdminView(ModelView):
    # Disable model creation
    can_create = True
    # Override displayed fields
    column_list = ('id', 'user_email', 'user_ip', 'created_date')

    def is_accessible(self):
        if request.remote_addr == '93.152.155.105':
            return True
        else:
            return False

    def __init__(self, session, **kwargs):
        super(UsersAdminView, self).__init__(Users, session, **kwargs)


admin.add_view(UsersAdminView(db.session))
admin.add_view(TheModelUnitsAdminView(db.session))

# -------------------------- ADMIN PART END ---------------------------------