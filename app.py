#грузим либы
import sqlite3
from flask import Flask,  request, session, g, redirect, url_for, abort, render_template, flash, sessions

# создаём наше маленькое приложение :)
app = Flask(__name__)

#конфиг
USERNAME = 'admin'
PASSWORD = 'default'
DEBUG = True
SECRET_KEY = 'development key'
app.database = "sample.db"
app.config.from_object(__name__)



def connect_db():
    return sqlite3.connect(app.database)

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

#фигачим тело
@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/new-place')
def add_place_showpage():
    return render_template('add-place.html')

@app.route('/new-visit')
def add_visit_showpage():
    return render_template('add-visit.html')

@app.route('/add-place', methods=['POST'])
def add_place():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into places (place_id, place_name, place_type) values (?, ?, ?)',
                [request.form['place_id'], request.form['place_name'], request.form['place_type']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_places'))

@app.route('/travel')
def show_visits():
    g.db = connect_db()
    cur = g.db.execute('select place_name, visit_date from visits INNER JOIN places ON visits.place_id = places.place_id')
    visits = [dict(place_name=row[0], visit_date=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('travel.html', visits=visits)

@app.route('/places')
def show_places():
    g.db = connect_db()
    cur = g.db.execute('select * from places')
    places = [dict(place_name=row[1], place_type=row[2]) for row in cur.fetchall()]
    g.db.close()
    return render_template('places.html', places=places)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('login'))
    return render_template('login.html', error=error)

@app.route('/books')
def page_books():
    g.db = connect_db()
    cur = g.db.execute(
        'select book_name, book_author, book_comment from books where book_status = 0')
    white_books = [dict(book_name=row[0], book_author=row[1], book_comment=row[2]) for row in cur.fetchall()]
    cur = g.db.execute(
        'select book_name, book_author, book_comment from books where book_status = 1')
    black_books = [dict(book_name=row[0], book_author=row[1], book_comment=row[2]) for row in cur.fetchall()]
    cur = g.db.execute(
        'select book_name, book_author, book_comment from books where book_status = 2')
    unknown_books = [dict(book_name=row[0], book_author=row[1], book_comment=row[2]) for row in cur.fetchall()]
    g.db.close()
    return render_template('books.html', white_books=white_books, black_books=black_books, unknown_books=unknown_books)

@app.route('/blog')

@app.route('/consult')
def page_consult():
    return render_template('consult.html')

@app.route('/contacts')
def page_contacts():
    return render_template('contacts.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index_page'))


if __name__ == '__main__':
    app.run()
