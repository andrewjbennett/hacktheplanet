# -*- coding: utf-8 -*-

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
import os
basedir = os.path.abspath(os.path.dirname(__file__))

from app import views, models

def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'sqlite_db'):
        sqlite_db = sqlite3.connect(app.config['DATABASE'])
        sqlite_db.row_factory = sqlite3.Row
        top.sqlite_db = sqlite_db

    return top.sqlite_db


@app.teardown_appcontext
def close_db_connection(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'sqlite_db'):
        top.sqlite_db.close()







@app.route('/register')
def register():
    db = get_db()
    cur = db.execute('select * from users order by id desc')
    users = cur.fetchall()

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select * from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

@app.route('/add_names')
def add_names():
    db = get_db()
    cur = db.execute('select * from entries order by id desc')
    entries = cur.fetchall()
    return render_template('add_names.html', entries=entries)

@app.route('/verify', methods=['GET', 'POST'])
def verify_names():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if request.method == 'POST':
        db.execute('update entries set verified = 1 where (id) = (?)',
            [request.form['id']])
        db.commit();
        flash('User verified!')
        return redirect(url_for('verify_names'))
    elif request.method == 'GET':
        cur = db.execute('select * from entries order by id desc')
        entries = cur.fetchall()
        return render_template('verify_names.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (name, nickname, school, age, verified) values (?, ?, ?, ?, ?)',
[request.form['name'], request.form['nickname'], request.form['school'], request.form['age'],0])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
#    if request.method == 'POST':
#        if request.form['username'] != app.config['USERNAME']:
#            error = 'Invalid username'
#        elif request.form['password'] != app.config['PASSWORD']:
#            error = 'Invalid password'
#        else:
#            session['logged_in'] = True
#            flash('You were logged in')
#            return redirect(url_for('show_entries'))
    form = LoginForm()
    if form.validate_on_submit():
      flash('Login requested')
      return redirect('/index')

    return render_template('login.html', error=error, form=form)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
#    init_db()
    app.run()
