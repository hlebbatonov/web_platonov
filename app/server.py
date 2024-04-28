from flask import render_template
from flask import Flask
from flask import redirect
from flask import request
from forms.user import RegisterForm, LoginForm
from data.users import User, Table
from data import db_session
from flask_login import LoginManager, login_user, current_user
import os
import datetime
from werkzeug.utils import secure_filename
from data.table_loader import view
from timetable_db import timetable_edit

host = '127.0.0.1'
port = 5000
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSION = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['PERMANENT_SESSION_LIFETIME'] = False


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("data/users.db")
    app.run(debug=True, host=host, port=port)


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        date = request.form.get()
        print(timetable_edit.table_for_user())

    return render_template("index.html", curr_date=str(datetime.date.today()))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
        return render_template('login.html', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if not os.path.exists(f'{app.config["UPLOAD_FOLDER"]}'):
            os.makedirs(f'{app.config["UPLOAD_FOLDER"]}')
        table = request.files['table']

        filename = secure_filename(table.filename)
        if table and allowed_file(table.filename):
            table.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
        abspath = str(os.path.abspath(f"{app.config['UPLOAD_FOLDER']}/{table.filename}")).replace('\\', '/')
        timetable_edit.add(view(abspath))
        return redirect("/admin_success")
    return render_template('admin.html')


@app.route('/admin_success')
def admin_success():
    return render_template('admin_success.html')


if __name__ == '__main__':
    main()
