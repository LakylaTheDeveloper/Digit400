from flask import Flask, render_template, flash, request, url_for, redirect, request, session, make_response, send_file, send_from_directory, jsonify
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from datetime import datetime,timedelta
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import gc
from functools import wraps
from content_management import Content
from db_connect import connection
APP_CONTENT = Content()


UPLOAD_FOLDER = '/var/www/FlaskApp/FlaskApp/uploads'
ALLOWED_EXTENTIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__, instance_path='/var/www/FlaskApp/FlaskApp/uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("please login.")
            return redirect(url_for('login'))
    return wrap

#upload file checker: "never trust user input"
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods = ["GET", "POST"])
def main():
    return render_template("main.html")

@app.route("/demo/", methods = ["GET", "POST"])
def demo():
    return render_template("game.html")

@app.route("/buy/", methods = ["GET", "POST"])
@login_required
def buy():
    return render_template("buy.html")

@app.route("/mail/", methods = ["GET", "POST"])
def email():
    try:
        return render_template("email.html")
    except Exception as e:
        return(str(e))

@app.route("/dashboard/")
@login_required
def dashboard():
    flash("This is a Flask Notification!")
    return render_template("dashboard.html", APP_CONTENT = APP_CONTENT)
  
@app.route('/introduction-to-app/')
@login_required
def introapp():
    try:
        output = ['Digit 400 is good !', 'Python, java, php,\ C++ ','<p><strong>Hello World! <strong><p>',42, '42']
        
        return render_template("templating_demo.html", output = output)
    
    except Exception as e:
        return(str(e))

@app.route('/background_process/')
@login_required
def background_process():
    try:
        lang = request.args.get('proglang', 0, type=str)
        if lang.lower() == 'python':
            return jsonify(result="You are wise!")
        else:
            return jsonify(result='try again.')
    except Exeption as e:
        return str(e)
    
@app.route('/jsonify/', methods=['GET', 'POST'])
@login_required
def json_stuff():
    return render_template("jsonify.html")
    
	

    
@app.route('/uploads/', methods=['GET', 'POST'])
@login_required
def upload_file():
    try:
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash ('No file part')
                return redirect(request.url)
            file = request.file['file']
            # if user does not select file, brower also summit a empty part without filename
            if file.filename == '':
                flash('No Selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File upload successful')
                return render_template('uploads.html', filename = filename)
        return render_template('uploads.html')
    except:
        flash("please upload a vaild file")
        return render_template('uploads.html')

@app.route('/download/')
@login_required
def download():
	try:
		return send_file('/var/www/FlaskApp/FlaskApp/uploads/screencap.png', attachment_filename='screencap.png')
	except Exception as e:
		return str(e)

@app.route('/downloader/', methods=['GET', 'POST'])
@login_required
def downloader():
    error = ''
    try:
        if request.method == "POST":
            filename = request.form['filename']
            return send_file('/var/www/FlaskApp/FlaskApp/uploads/' + filename, attachment_filename='download')

        else:
            return render_template('downloader.html', error = error)
        error = "Please enter a valid file name"
        return render_template('downloader.html',error = error)

    except:
        error = "Please enter a valid file name"
        return render_template('downloader.html',error = error)


@app.route("/login/", methods = ["GET", "POST"])
def login():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":
            data =  c.execute("SELECT * FROM users WHERE username = ('{0}')".format(thwart(request.form['username'])))
            data = c. fetchone()[2]
            
            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']
                
                flash("You are now logged in!")
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Credentials. Please Try Again."
                
                gc.collect()
                return render_template("login.html", error = error)
        
        if request.method == "POST":
            entered_username = request.form['username']
            entered_password = request.form['password']

            if entered_username == "demo" and entered_password == "demo":
                flash("Howdy, " + entered_username)
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid Credentials. Please Try Again."

        return render_template("login.html", error = error)

    except Exception as e:
        flash(e) #delete upon release. for debugging purposes only!
        return render_template("login.html", error = error)

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out *insert name here* !")
    gc.collect()
    return redirect(url_for('main'))
    
    
    
class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice', [validators.Required()])

    
    
@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = ('{0}')".format((thwart(username))))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES ('{0}','{1}','{2}','{3}')".format(thwart(username), thwart(password), thwart(email), thwart("/dashboard/")))

                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))


@app.route('/sitemap.xml/', methods=['GET'])
def sitemap():
    try:
        pages = []
        week = (datetime.now() - timedelta(days = 7)).date().isoformat()
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments)==0:
                pages.append(
                    ["http://174.138.86.46"+str(rule.rule),week]
                )
        sitemap_xml = render_template('sitemap_template.xml', pages = pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        return(str(e))    
    
@app.route('/robots.txt/')
def robots():
    #return("User-agent: *\nDisallow /") #Disallows all robot traffic
    return("User-agent: *\nDisallow: /register/\nDisallow: /login/") #Disallows robot traffic to sensitive urls
    
@app.route('/about/')
def about():
    return render_template("about.html")
    
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html")

@app.errorhandler(500)
def int_server_error(e):
    return render_template("500.html", error = e)
    
    

if __name__ == "__main__":
	app.run()
    
    
    
    