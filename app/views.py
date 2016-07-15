# -*- coding: utf-8 -*-

from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, _app_ctx_stack
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask.ext.wtf import Form
from flask.ext.login import login_user, logout_user, current_user, login_required

from app import app, models, forms
from .data import db, query_to_list
from .forms import * 
from .models import *

def recalculate_points():
  users = User.query.all()
  for user in users:
    print "user: %r" % (user)
    points = 0
    flags_scored = Flags_scored.query.filter(Flags_scored.user_id==user.id).all() 
    for flag in flags_scored:
      print "points before: %d" % (points)
      points += Flags.query.filter(Flags.id == flag.flag_id).first().points
      print Flags.query.filter(Flags.id == flag.flag_id).first()
      print "points after: %d, flag id %d" % (points, flag.flag_id)
    user.points = points
    db.session.add(user)
  db.session.commit()

def setup_max_levels(user):
  games = Wargames.query.all()

  for game in games:
    print "game: %r" % (game)
    flags_maxlevel = Flags_maxlevel()
    flags_maxlevel.user_id = user.id
    flags_maxlevel.wargame_id = game.id
    flags_maxlevel.maxlevel = 0
    db.session.add(flags_maxlevel)
    print "setup max levels: adding to db"
  db.session.commit()

def setup_max_levels_new_wargame(wargame):
    users = User.query.all()

    print "starting setup max levels for new wargame"
    for user in users:
        print "user %r "% (user)
        flags_maxlevel = Flags_maxlevel()
        flags_maxlevel.user_id = user.id
        flags_maxlevel.wargame_id = wargame.id 
        flags_maxlevel.maxlevel = 0
        db.session.add(flags_maxlevel)
    db.session.commit()

# this function only gets called right after an object has been made, which
# will contain a maxlevel
def add_all_flags(wargame):
    # go through each level from 0 to maxlevel and set them all to defaults
    for i in range(0,wargame.maxlevel):
        flag = Flags(wargame_id=wargame.id, 
                     level=i)
        db.session.add(flag)
    db.session.commit() 


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
def index():
  if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('profile'))
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('profile'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        login_user(User.query.filter_by(username=form.username.data).first())
        return redirect('/profile')
    error = form.errors

    return render_template('login.html', error=error, form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User()
    form.populate_obj(user)
    if form.ctfteam.data:
      user.ctfteam = 1
    else:
      user.ctfteam = 0
    db.session.add(user)
    db.session.commit()
    login_user(user)
    setup_max_levels(user)
    return redirect(url_for('profile')) # something?
  return render_template('register.html', form=form)


@app.route('/profile')
@login_required
def profile():
  # check logged in

  # render profile template -- get logged in user, 
  # get their points, show them all

  # find all their wargames max levels

  # TIL: db.session.query(blah) otherwise you get just a user object.
  max_levels = db.session.query(User.id, Flags_maxlevel.maxlevel, Wargames.name)\
          .join(Flags_maxlevel, User.id == Flags_maxlevel.user_id).\
          join(Wargames, Wargames.id == Flags_maxlevel.wargame_id)\
          .filter(User.username==g.user.username).all()

  print "in profile: user., ppoints"
  print g.user
  print g.user.points
  return render_template('profile.html', user=g.user, max_levels=max_levels)

@app.route('/profile/<username>')
@login_required
def user_profile(username):
  user = User.query.filter(User.username==username).first()
  flags_solved = db.session.query(Flags_scored,Wargames.name,Flags.level,Flags.points).join(Flags, Flags.id==Flags_scored.flag_id)\
    .join(Wargames, Wargames.id == Flags.wargame_id).filter(Flags_scored.user_id==user.id).all()

  print "hello*******************************"
  print db.session.query(Flags_scored,Wargames.name,Flags.level,Flags.points).join(Flags, Flags.id==Flags_scored.flag_id)\
    .join(Wargames, Wargames.id == Flags.wargame_id).filter(Flags_scored.user_id==user.id)
  print "hello*******************************"

  # obj, name, level, points
  
  return render_template("flags.html", flags=flags_solved, user=user)



@app.route('/profile/flags')
@login_required
def profile_flags():
  flags_solved = db.session.query(Flags_scored,Wargames.name,Flags.level,Flags.points).join(Flags, Flags.id==Flags_scored.flag_id)\
    .join(Wargames, Wargames.id == Flags.wargame_id).filter(Flags_scored.user_id==g.user.id).all()

  # obj, name, level, points
  
  return render_template("flags.html", flags=flags_solved, user=g.user)

@app.route('/logout/')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))


@app.route('/admin')
@login_required
def admin():
  # check the user is an admin
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))

  return render_template('admin.html', user=g.user)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_wargame():
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))
  
  form = AddWargameForm()
  if form.validate_on_submit():
      wargame = Wargames()
      form.populate_obj(wargame)
      db.session.add(wargame)
      db.session.commit()
      # create a function to add this to everyone at level 0
      print "wargame, maxlevel"
      print wargame
      print wargame.maxlevel
      setup_max_levels_new_wargame(wargame)
      add_all_flags(wargame)
      flash("Successfully added!")
      return redirect(url_for('admin'))

  errors = form.errors

  return render_template('add_wargame.html', error=errors, form=form)

@app.route('/admin/edit/<wargame>', methods=['GET', 'POST'])
@login_required
def edit_wargame(wargame):
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))

  wg = Wargames.query.filter(Wargames.name==wargame).first()
  if wg is None:
    flash("invalid name")
    return redirect(url_for('admin'))

  form = EditWargameForm(obj=wg)
  if form.validate_on_submit():
    wg.info = form.info.data
    db.session.add(wg)
    db.session.commit()
    print "adding info to wargame %s" % (wargame)
    flash("Successfully fixed!")
    return redirect(url_for("admin"))
  errors = form.errors
  return render_template('edit_wargame.html', error=errors, form=form, wargame=wargame)



@app.route('/admin/edit/<wargame>/<int:level_number>', methods=['GET','POST'])
@login_required
def edit_flag(wargame, level_number):
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))

  # look up wargame by name
  wg = Wargames.query.filter(Wargames.name==wargame).first()
  if wg is None or wg.maxlevel < level_number:
    flash("Invalid wargame or level too high, wargame is %s, level is %d, wg is %s, maxlevel is %d" % (wargame, level_number, wg, wg.maxlevel))
    return redirect(url_for('list_wargames'))

  # make a form for editing the flag which gets prefilled with existing  


  flag = db.session.query(Flags).filter(Flags.wargame_id==wg.id).filter(Flags.level==level_number).one()

  print "flag: "
  print flag

  if not flag:
    flash("error, no such flag exists")
    return redirect(url_for("admin"))

  form = EditLevelForm(obj=flag)
  if form.validate_on_submit():
    flag.flag = form.flag.data
    flag.points = form.points.data
    db.session.add(flag)
    db.session.commit()
    flash("successfully changed the flag")
    return redirect(url_for("list_wargames"))

  error = form.errors

  return render_template('edit_flag.html', form=form, error=error, wargame=wargame, level_number=level_number)

@app.route('/propose/<wargame>/<int:level_number>', methods=['GET', 'POST'])
@login_required
def propose_flag(wargame, level_number):
  flag_id = db.session.query(Flags.id)\
            .join(Wargames, Wargames.id == Flags.wargame_id)\
            .filter(Flags.level == level_number)\
            .filter(Wargames.name==wargame)\
            .first()

  if flag_id:
    flag_id = flag_id[0]
    print "flag id: %r" % flag_id
  else:
    flash("Invalid flag")
    return redirect(url_for("profile"))

  form = ProposeFlagForm()
  if form.validate_on_submit():
    data = db.session.query(Flags.id, Wargames.id)\
      .join(Wargames, Wargames.id == Flags.wargame_id)\
      .filter(Flags.level == level_number)\
      .filter(Wargames.name==wargame)\
      .first()

    proposed = Flags_proposed(flag=form.flag.data, wargame_id=data[1], 
                flag_id=data[0], user_id=g.user.id)

    db.session.add(proposed)
    db.session.commit()
    flash("Successfully submitted!")
    return redirect(url_for("profile"))
  
  return render_template("propose_flag.html", wargame=wargame, level_number=level_number, form=form, error=form.errors)


@app.route('/submit/<wargame>/<int:level_number>', methods=['GET', 'POST'])
@login_required
def submit_flag(wargame, level_number):
  # check that they haven't already submitted this level
  max_levels = db.session.query(Wargames.id, Flags_maxlevel.maxlevel, Wargames.name, Flags_maxlevel.wargame_id)\
          .join(Flags_maxlevel, g.user.id == Flags_maxlevel.user_id).\
          join(Wargames, Wargames.id == Flags_maxlevel.wargame_id)\
          .filter(User.username==g.user.username)\
          .filter(Wargames.name==wargame).first()
          
  print "wargame %r, level number %r" % (wargame, level_number)
  print "max levels 1, levle number"
  print max_levels[1]
  print level_number
  if max_levels[1] > level_number:
      flash("You've already completed this level! Records show you've completed %d and you're trying to complete %d" % (int(max_levels[1]), level_number))
      return redirect(url_for("profile"))

  # check that they've solved level n-1 OR this is level 0
  if level_number != 0 and level_number != max_levels[1]:
      flash("You need to solve the previous level first!")
      return redirect(url_for("profile"))


  # get the flag id for real
  print 'OY', db.session.query(Flags.id).join(Wargames, Wargames.id == Flags.wargame_id).filter(Flags.level == level_number).filter(Wargames.name==wargame).all()
  print 'OY', db.session.query(Flags.id).join(Wargames, Wargames.id == Flags.wargame_id).filter(Flags.level == level_number).filter(Wargames.name==wargame)

  flag_id_for_real = db.session.query(Flags.id)\
          .join(Wargames, Wargames.id == Flags.wargame_id)\
          .filter(Flags.level == level_number)\
          .filter(Wargames.name==wargame)\
          .first()
  if flag_id_for_real:
    print "flag id exists"
    print flag_id_for_real
    flag_id_for_real = flag_id_for_real[0]
  else:
    print "flag id doesn't exist"
  

  print "flag id for real: %d" % (flag_id_for_real)

  a_flag_id_for_real = db.session.query(Flags.id,Wargames.name)\
          .join(Wargames, Wargames.id == Flags.wargame_id)\
          .filter(Flags.level == level_number)\
          .first()[1]

  print "wargame name db: %r" % (a_flag_id_for_real)

  wargame_info = db.session.query(Wargames.info).filter(Wargames.name==wargame).first()
  print "wargame info %r" % (wargame_info)

  error = ""
  # show the form to submit this level 
  form = SubmitFlagForm()
  if form.validate_on_submit():
    correct = db.session.query(Flags, Wargames)\
           .join(Wargames, Wargames.id == Flags.wargame_id)\
           .filter(Flags.flag == form.flag.data)\
           .filter(Wargames.name == wargame)\
           .filter(Flags.level == level_number).first()
    attempt = Flags_attempted(flag_id=flag_id_for_real,
                              user_id=g.user.id,
                              correct=0,
                              flag=form.flag.data)
    if correct is None:
        error += "Incorrect flag..."
        db.session.add(attempt)
        db.session.commit()
        return render_template('submit_flag.html', form=form, error=error, wargame=wargame, level_number=level_number)
    
    # they got it right, so add to the db
    attempt.set_correct(correct=1)
    scored = Flags_scored(flag_id=flag_id_for_real,
                          user_id=g.user.id)

    db.session.add(scored)
    db.session.add(attempt)
    db.session.commit()
    flash("Correct! Well done")
    
    # update the max level
    max_level_thing = db.session.query(Flags_maxlevel)\
            .filter(Flags_maxlevel.wargame_id==max_levels[3],
                    Flags_maxlevel.user_id==g.user.id)\
            .one()
    max_level_thing.maxlevel += 1
    db.session.add(max_level_thing)
    db.session.commit()
   
    # update the user's points

    points = db.session.query(Flags.points).filter(Flags.id==flag_id_for_real).one()
    user = db.session.query(User).filter(User.id==g.user.id).one()
    print "points, user: "
    print points
    print user
    user.points += points[0]
    print "adding %d points to %d", points[0], user.points
    db.session.add(user)
    db.session.commit()

    return redirect(url_for("profile"))

        
  return render_template('submit_flag.html', form=form, error=form.errors,wargame=wargame,level_number=level_number, info=wargame_info)



@app.route('/admin/list/users')
@login_required
def list_users():
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))

  return render_template('list_users.html')

@app.route('/admin/list/wargames')
@login_required
def list_wargames():
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))

  # show all of the wargames with a link to their level

  wargames = Wargames.query.all()

  return render_template('list_wargames.html', wargames=wargames, max_levels=[])

@app.route('/admin/list/proposed')
@login_required
def list_proposed():
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))
  
  proposed = db.session.query(Flags_proposed, Wargames.name, Flags.level)\
              .join(Wargames, Wargames.id==Flags_proposed.wargame_id)\
              .join(Flags, Flags.id==Flags_proposed.flag_id)\
              .all()


  return render_template('list_proposed.html', proposed=proposed)


@app.route('/admin/fix')
@login_required
def fix_points():
  if g.user is None or g.user.role != 1:
    return redirect(url_for('profile'))
  recalculate_points()  
  flash("Recalculated points!")
  return redirect(url_for('admin'))

@app.route('/leaderboard')
@login_required
def leaderboard():
  users = db.session.query(User).filter(User.ctfteam==0).order_by(User.points.desc()).all()
  ctfteam = db.session.query(User).filter(User.ctfteam==1).order_by(User.points.desc()).all()
  return render_template('leaderboard.html', users=users, ctfteam=ctfteam, user=g.user)

