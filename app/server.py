from flask import render_template
from flask import Flask
from flask import redirect
from flask import request
from forms.user import RegisterForm, LoginForm, Date
from data.users import User, Table
from data import db_session
from flask import send_file
from flask_login import LoginManager, login_user, current_user, logout_user
import os
import datetime
from werkzeug.utils import secure_filename
from data.table_loader import view
from timetable_db import timetable_edit
from files_for_converting import files_conventer
import csv
import convertapi
host = '127.0.0.1'
port = 5000
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSION = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
curr_user_group = ''
curr_user_is_admin = 0
user_timetable = []
# app.config['PERMANENT_SESSION_LIFETIME'] = False


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(int(user_id))


def main():
    db_session.global_init("data/users.db")

    admin = User(
        name='admin',
        email='admin@timetable.ru',
        about='admin'
    )
    admin.set_password('4gc3C-ld55')
    db_sess = db_session.create_session()
    if not db_sess.query(User.email).filter(User.email == 'admin@timetable.ru').first():
        db_sess.add(admin)
        db_sess.commit()
    app.run(debug=True, host=host, port=port)


# ...
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    global user_timetable
    if curr_user_is_admin != 0:
        return redirect('/admin')
    else:
        form = Date()
        if form.validate_on_submit():
            error_date = str(form.date.data)
            date = str(form.date.data)[8] + str(form.date.data)[9] + '.' + str(form.date.data)[5] + str(form.date.data)[
                6] + '.' + str(form.date.data)[0] + str(form.date.data)[1] + str(form.date.data)[2] + str(form.date.data)[3]
            user_timetable = list(map(lambda x: list(x), timetable_edit.table_for_user(date, curr_user_group)))
            print(user_timetable)
            if user_timetable == []:
                return render_template("index.html", form=form, curr_date=error_date, timetable_is_not_found=1)
            else:
                return render_template("index.html", form=form, curr_date=error_date, timetable_is_not_found=0,
                                       user_timetable=user_timetable, button_not_pushed=0, group=curr_user_group, date=date)
        return render_template("index.html", form=form, curr_date=str(datetime.date.today()), timetable_is_not_found=0,
                               button_not_pushed=1)
@app.route('/download_timetable', methods=['GET'])
def download_timetable():
    with open(f'files_for_converting/export.csv', encoding='utf-8', mode='w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['time', 'subject', 'place'])
        for i in user_timetable:
            i = list(map(lambda x: f'"{x}"', i))
            writer.writerow(i)
    convertapi.api_secret = 'm79kk5eVwEENi0pB'
    convertapi.convert('pdf', {
        'File': 'files_for_converting/export.csv',
        'AutoFit': 'true',
        'Scale': '200'
    }, from_format='csv').save_files('files_for_converting/export/export.pdf')
    print('converted')
    path = os.path.abspath('files_for_converting\\export\\export.pdf')
    return send_file(path, as_attachment=False)

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
    global curr_user_is_admin
    global curr_user_group
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            curr_user_group = db_sess.query(User.about).filter(User.email == form.email.data).first()[0]
            if str(user.email) == 'admin@timetable.ru':
                curr_user_is_admin = 1
                return redirect('/admin')
            return redirect("/")

        return render_template('login.html', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global curr_user_is_admin
    if curr_user_is_admin == 0 or not current_user.is_authenticated:
        curr_user_is_admin = 0
        return redirect('/')
    else:
        if request.method == 'POST':
            if not os.path.exists(f'{app.config["UPLOAD_FOLDER"]}'):
                os.makedirs(f'{app.config["UPLOAD_FOLDER"]}')
            table = request.files['table']

            filename = secure_filename(table.filename)
            if table and allowed_file(table.filename):
                table.save(f"{app.config['UPLOAD_FOLDER']}/{filename}")
            abspath = str(os.path.abspath(f"{app.config['UPLOAD_FOLDER']}/{table.filename}")).replace('\\', '/')
            print(timetable_edit.add(view(abspath)))
            return redirect("/admin_success")
        return render_template('admin.html')


@app.route('/admin_success')
def admin_success():
    if curr_user_is_admin == 0:
        return redirect('/')
    else:
        return render_template('admin_success.html')


if __name__ == '__main__':
    main()
