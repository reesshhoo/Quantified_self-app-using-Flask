from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
login_manager = LoginManager(app)



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    linkers = db.relationship("Tracker", secondary="linker")

    def get_id(self):
        return self.user_id
    
class Tracker(db.Model):
    __tablename__ = 'tracker'
    tracker_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

class Linker(db.Model):
    __tablename__ = 'linker'
    linker_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.tracker_id"), nullable=False)
    tracker_value = db.Column(db.String, nullable=False)
    comments = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)



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

@app.route('/', methods=['GET', 'POST'])
def login_validation():
    global current_user
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
                    current_user = check1.username
                    login_user(check1, remember=True)
                    return redirect('/dashboard')
                else:
                    return render_template('welcome.html', error=1)
    except:
        return render_template('welcome.html', error=1)


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

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    track= Tracker.query.all()
    naam = User.query.filter_by(username=current_user).first()
    
    if request.method=='GET':
        lasttracked = datetime.now()
        return render_template('home.html', track=track,c=naam, lasttracked=lasttracked)

# @app.route('/add_tracker', methods=['POST'])
# def add_tracker():
    else:
        trackerlist = []
        lk = request.form.get('trackid')
        find = Tracker.query.filter_by(tracker_id=lk).first()
        trackerlist.append(find.tracker_name)
        lasttracked = datetime.now()
        return render_template('home.html', lasttracked=lasttracked, track=track, trackerlist=trackerlist,c=naam)

    
    
        





# @app.route('/add_log', methods=['GET', 'POST'])
# def add_log():



        
            








if __name__ == '__main__':
    app.run(debug=True)


