# ---------------------------------------------------------------- IMPORTS ----------------------------------------------------------------------------------- #

from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin


# ---------------------------------------------------------------- APP INTIALIZATION ----------------------------------------------------------------------------------- #

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
login_manager = LoginManager(app)


# ---------------------------------------------------------------- DATABASE MODEL CLASSES ----------------------------------------------------------------------------------- #
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    trackers = db.relationship("Tracker")

    def get_id(self):
        return self.user_id
    
class Tracker(db.Model):
    __tablename__ = 'tracker'
    tracker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    tracker_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    tracker_type = db.Column(db.String, nullable=False)
    options = db.Column(db.String, nullable=True, default=None)
    logs = db.relationship('Log')
    # settings = db.relationship('Setting', uselist=False)

    

class Log(db.Model):
    __tablename__ = 'logger'
    logger_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.tracker_id"), nullable=False)
    log_value = db.Column(db.String, nullable=False)
    comments = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.String, nullable=False, default=datetime.now())



# ---------------------------------------------------------------- LOGIN REQUIRED----------------------------------------------------------------------------------- #

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(user_id=user_id).first()


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
    
    # ---------------------------------------------------------------- LOGIN AUTHENTICATION----------------------------------------------------------------------------------- #

@app.route('/', methods=['GET', 'POST'])
def login_validation():
    global check1
    try:
        if request.method=='GET':
            return render_template('welcome.html')
        else:
            
            usr = request.form.get('username')
            pasw = request.form.get('password')
            check1 = User.query.filter_by(username=usr).first()
            check2 = User.query.filter_by(password=pasw).first()
            
            if (usr=='') or (pasw==''):
                return render_template('welcome.html', error=1)
            else:
                if check1.user_id==check2.user_id:
                    login_user(check1, remember=True)
                    return redirect(f'/dashboard/{check1.user_id}')
                else:
                    return render_template('welcome.html', error=1)
    except:
        return render_template('welcome.html', error=1)

# ---------------------------------------------------------------- REGISTRATION----------------------------------------------------------------------------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method=='GET':
            return render_template('register.html')
        if request.method=='POST':
            name = request.form.get('uname')
            pswrd = request.form.get('upass')
            existing_user = User.query.filter_by(username=name).first()
            if existing_user is not None:
                return render_template('register.html', error=1)
            else:
                new_user = User(username=name, password=pswrd)
                db.session.add(new_user)
                db.session.commit()
    except:
        return render_template('register.html', error=1)

    return redirect('/')

# ---------------------------------------------------------------- DASHBOARD ----------------------------------------------------------------------------------- #

@app.route('/dashboard/<int:uid>', methods=['GET', 'POST'])
@login_required
def dashboard(uid):
    if request.method=='GET':
        trackers=User.query.filter_by(user_id=uid).first()
        return render_template('home.html', c=trackers, trackers=trackers.trackers)




# ---------------------------------------------------------------- ADD TRACKER ----------------------------------------------------------------------------------- #


@app.route('/add_tracker/<int:uid>', methods=['POST'])
def addtracker(uid):
    if request.method=='POST':
        t_name = request.form.get('tname')
        t_desc = request.form.get('tdesc')
        t_type = request.form.get('ttype')
        if t_type=='Multi-choice':
            t_options= request.form.get('toptions')
            track = Tracker(tracker_name=t_name, description=t_desc, tracker_type=t_type, user_id=uid ,options=t_options)
        else:
            track = Tracker(tracker_name=t_name, user_id=uid, description=t_desc, tracker_type=t_type)
        db.session.add(track)
        db.session.commit()

    return redirect(f'/dashboard/{uid}')
        
# ---------------------------------------------------------------- LOG REGISTER ----------------------------------------------------------------------------------- #

@app.route("/logs/<int:tid>", methods=["GET", "POST"])
def logs(tid):
    track = Tracker.query.filter_by(tracker_id=tid).first()
    trackers=User.query.filter_by(user_id=track.user_id).first()
    if request.method == "GET":
        loggers=Log.query.filter_by(tracker_id=tid).all()
        return render_template("logs.html", track=track,c=trackers, d=trackers.trackers, loggers=loggers)
    else:
        ttime = request.form.get("ttime")
        tcomm = request.form.get("tcomm")
        print('\n', track.tracker_type, "\n")
        if track.tracker_type == "Multi-choice":
            ttype = request.form["ltype"]
            log = Log(log_value=ttype, comments=tcomm, tracker_id=tid, timestamp=ttime)

        else:

            tval = request.form.get("tval")
            log = Log(log_value=tval, comments=tcomm, tracker_id=tid, timestamp=ttime)
        db.session.add(log)
        db.session.commit()
    loggers=Log.query.filter_by(tracker_id=tid).all()

    return render_template("logs.html", track=track,c=trackers, loggers=loggers)

# ---------------------------------------------------------------- UPDATE TRACKER ----------------------------------------------------------------------------------- #

@app.route('/update_tracker/<int:tid>', methods=['GET','POST'])
def update_tracker(tid):
    trackfil = Tracker.query.filter_by(tracker_id=tid).first()
    if request.method=='GET':
        
        return render_template('update_tracker.html', trackfil=trackfil)
    else:
        newtname = request.form.get('newtname')
        newtdesc = request.form.get('newtdesc')
    
        trackfil.tracker_name = newtname
        trackfil.description = newtdesc
        db.session.add(trackfil)
        db.session.commit()
        return redirect(f'/dashboard/{trackfil.user_id}')

# ---------------------------------------------------------------- DELETE TRACKER ----------------------------------------------------------------------------------- #

@app.route('/delete_tracker/<int:tid>')
def delete_tracker(tid):
    trackfil = Tracker.query.filter_by(tracker_id=tid).first()
    trackers=User.query.filter_by(user_id=trackfil.user_id).first()
    Tracker.query.filter_by(tracker_id=tid).delete()
    Log.query.filter_by(tracker_id=tid).delete()
    db.session.commit()
    return redirect(f'/dashboard/{trackers.user_id}')

# ---------------------------------------------------------------- UPDATE LOG ----------------------------------------------------------------------------------- #

@app.route('/update_log/<int:tid>', methods=['GET','POST'])
def update_log(tid):
    logfil = Log.query.filter_by(tracker_id=tid).first()
    trackfil = Tracker.query.filter_by(tracker_id=tid).first()
    if request.method=='GET':
        return render_template('update_log.html', logfil=logfil, trackfil=trackfil)
    else:
        newtime = request.form.get('newtime')
        newcomm = request.form.get('newcomm')

        logfil.tracker_name = newtime
        logfil.description = newcomm
        logfil.timestamp = newtime
        logfil.comments = newcomm
        if trackfil.tracker_type=='Numerical':
            newval = request.form.get('newval')
            logfil.log_value = newval
        else:
            newchoice = request.form.get('newchoice')
            logfil.log_value = newchoice
        
        db.session.add(logfil)
        db.session.commit()
        return redirect(f'/logs/{tid}')

    
    # ---------------------------------------------------------------- DELETE LOG ----------------------------------------------------------------------------------- #


@app.route('/delete_log/<int:lid>')
def delete_log(lid):
    logfil = Log.query.filter_by(logger_id=lid).first()
    # logger=User.query.filter_by(user_id=trackfil.user_id).first()
    # logfil = Log.query.filter_by(tracker_id=tid).all()
    Log.query.filter_by(logger_id=lid).delete()
    # Log.query.filter_by(tracker_id=tid).delete()
    # db.session.delete(logfil)
    db.session.commit()
    return redirect(f'/logs/{logfil.tracker_id}')






# ---------------------------------------------------------------- RUNNING THE APP ----------------------------------------------------------------------------------- #




if __name__ == '__main__':
    app.run(debug=True)


