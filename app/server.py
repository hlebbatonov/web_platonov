from flask import render_template
from flask import Flask
from flask import redirect
from flask import session
from forms.user import RegisterForm, LoginForm
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
host = '127.0.0.1'
port = 5000
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

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

    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    #if current_user.is_authenticated:
    #    return redirect('/')
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
    #if current_user.is_authenticated:
    #    return redirect('/')
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
    return render_template('admin.html')
if __name__ == '__main__':
    main()

