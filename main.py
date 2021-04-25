import datetime
import webbrowser

from flask import Flask, render_template, redirect, make_response, request, session, abort
from data import db_session
from data.comments import Comment
from data.news import News
from data.users import User
from forms.comms import CommsForm
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

db_session.global_init("db/blogs.db")

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template("index.html", news=news, title="main")


@app.route("/<int:id>")
def profile(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if current_user == user:

        news = db_sess.query(News).filter(News.user == user)
    else:
        news = db_sess.query(News).filter((News.user == user), (News.is_private != True))
    if user:
        ...
    else:
        abort(404)

    return render_template('profile.html',
                           title=f'{user.name}',
                           user=user, news=news)


@app.route("/portfolio/<int:id>", methods=["GET", "POST"])
def portfolio(id):
    form = NewsForm()
    form_comm = CommsForm()
    db_sess = db_session.create_session()
    news_id = db_sess.query(News).filter(News.id == id).first()
    user = db_sess.query(User).filter(news_id.user_id == User.id).first()
    comms = db_sess.query(Comment).filter(news_id.id == Comment.news_id)
    if not user:
        abort(404)
    if form.validate_on_submit():
        if current_user.is_authenticated():
            if form.comment.data == "" or form.comment.data is None:
                render_template("portfolio.html",
                                title=f"Портфолио пользователя {user.name}",
                                form=form, user=user, news=news_id, comms=comms,
                                form_comm=form_comm, message="Enter your comment")

            comment = Comment(
                commentary=form.comment.data,
                news_id=id,
                user_id=user.id,
                is_private=form.anonymous.data
            )
            db_sess.add(comment)
            db_sess.commit()
            return redirect("/")
        else:
            render_template("portfolio.html",
                            title=f"Портфолио пользователя {user.name}",
                            form=form, user=user, news=news_id,
                            message="Sign in if you want to comment")

    return render_template("portfolio.html",
                           title=f"Портфолио пользователя {user.name}",
                           form=form, user=user, news=news_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
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


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.surname = form.surname.data
        news.name = form.name.data
        news.batya = form.batya.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res
    # delete
    # res.set_cookie("visits_count", '1', max_age=0)


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")
    # delete
    # session.pop('visits_count', None)


def main():
    # db shit
    # db_sess = db_session.create_session()

    # первый в выборке
    # user = db_sess.query(User).first()

    # # select
    # for user in db_sess.query(User).filter((User.id > 1) | (User.email.notlike("%1%"))):
    #     print(user)
    #
    # print()
    #
    # # replace smth
    # user = db_sess.query(User).filter(User.id == 1).first()
    # print(user)
    # user.name = "Измененное имя пользователя"
    # user.created_date = datetime.datetime.now()
    #
    # # delete
    # db_sess.query(User).filter(User.id >= 3).delete()
    # # or
    # user = db_sess.query(User).filter(User.id == 2).first()
    # db_sess.delete(user)

    # fill table
    # for i in range(1, 4):
    #     user = User()
    #     user.name = f"Пользователь {i}"
    #     user.about = f"биография пользователя {i}"
    #     user.email = f"email{i}@email.ru"
    #     db_sess.add(user)
    #
    # # NEWS TABLE
    # news = News(title="Первая новость", content="Привет, блог!",
    #             user_id=1, is_private=False)
    # db_sess.add(news)
    #
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="second news", content="second note!",
    #             user=user, is_private=False)
    # db_sess.add(news)
    #
    # user = db_sess.query(User).filter(User.id == 1).first()
    # news = News(title="Personal note", content="This note is private", is_private=True)
    # user.news.append(news)
    #
    # for news in user.news:
    #     print(news)

    # db_sess.commit()
    app.run(port=8080, host="127.0.0.1")


if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:8080/")
    main()




