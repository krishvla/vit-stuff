from flask import Flask,render_template,request, flash, redirect, url_for, session, logging
from flask_mysqldb import MySQL
from datetime import timedelta
from functools import wraps
from wtforms import Form, StringField, IntegerField, TextAreaField, PasswordField, validators, SelectField
from flask_wtf import FlaskForm
app = Flask(__name__)
app.secret_key = 'some secret key'
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=2)
#config MySQL
app.config['MYSQL_HOST']='xxxxxxxxxxxxxxxxxxxxxxx'
app.config['MYSQL_USER']='xxxxxxxxxxxxxxxxxxxx'
app.config['MYSQL_PASSWORD']='xxxxxxxxxxxxxxxxxxxxxxxxxx'
app.config['MYSQL_DB']='xxxxxxxxxxxxxxxxxxxxxxxxxx'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#initialize MySQL
mysql = MySQL(app)

#security
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized , Please Login', 'danger')
			return render_template('login.html')
	return wrap


#======================Forms==========================================
class Suggestion(Form):
	name = StringField('Name',[validators.Length(min=0,max=15)])
	sug= StringField('Suggestion',[validators.DataRequired()])
class addc(Form):
	course = StringField('Course Code',[validators.DataRequired()])
	cname = StringField('Course Name',[validators.DataRequired()])
class liup(Form):
	course = StringField('Course Code',[validators.DataRequired()])
	etype = SelectField('Type of Exam', choices = [('C1','CAT-1'),('C2','CAT-2'),('F','FAT')])
	upli = StringField('Updated Link',[validators.DataRequired()])
#=========================================End of Forms=========================================

@app.route('/')
def index():
 	return render_template('home.html')
@app.route('/about')
def About():
	return render_template('About.html')
@app.route('/Home')
def Home():
	return render_template('home.html')
@app.route('/upload')
def upload():
	return redirect('https://docs.google.com/forms/d/e/1FAIpQLSeuIFTvEIsJFoV9tW_9LyaEtwKe1m9I4QRyXwJ3q4n444qgaw/viewform?usp=sf_link')
@app.route('/browse')
def browse():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM courses")
	course = cur.fetchall()
	cur.close()
	return render_template('browse.html',course = course)

@app.route('/sub/<string:ccode>', methods=['GET', 'POST'])
def sub(ccode):
	cur = mysql.connection.cursor()
	cur.execute("SELECT link FROM drive WHERE ccode=%s and exam='C1'",[ccode,])
	result1 = cur.fetchall()
	print(len(result1))
	if len(result1)>0:
		cat1=result1
	else:
		cat1=0
	cur.execute("SELECT link FROM drive WHERE ccode=%s and exam='C2'",[ccode])
	result2 = cur.fetchall()
	if len(result2)>0:
		cat2=result2
	else:
		cat2=0
	cur.execute("SELECT link FROM drive WHERE ccode=%s and exam='F'",[ccode])
	result3 = cur.fetchall()
	if len(result3)>0:
		fat=result3
	else:
		fat=0
	cur.close()
	return render_template('subject.html',cat1=cat1,cat2=cat2,fat=fat)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		#Getting form fields
		login_id = request.form['login_id']
		password_candidate = request.form['password']
		if login_id == 'xxxxxxxxxxxxxxxxxxx' and password_candidate == 'xxxxxxxxxxx':
			session['logged_in'] = True
			session['login_id'] = login_id
			cur = mysql.connection.cursor()
			cur.execute("SELECT * FROM courses")
			tc = cur.fetchall()
			cur.execute("SELECT * FROM drive")
			td= cur.fetchall()
			return render_template('admin.html',tc=tc,td=td)
		else:
			flash("Only For Admins!",'danger')
	return render_template('login.html')

@app.route('/newcourse',methods=['GET', 'POST'])
@is_logged_in
def newcourse():
	#import register()
	form = addc(request.form)
	if request.method == 'POST' and form.validate():
		course = form.course.data
		cname = form.cname.data
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO courses(ccode, name)VALUES(%s, %s)", (course, cname))
		mysql.connection.commit()
		cur.close()
		flash('Added Successfully!!!', 'success')
		redirect(url_for('newcourse'))
	return render_template('addcourse.html',form=form)
@app.route('/linkup',methods=['GET', 'POST'])
@is_logged_in
def linkupdate():
	#import register()
	form = liup(request.form)
	if request.method == 'POST' and form.validate():
		course = form.course.data
		etype = form.etype.data
		uplink = form.upli.data
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM drive WHERE ccode=%s and exam=%s",[course, etype])
		n = cur.fetchone()
		if n>0:
			cur.execute("UPDATE drive SET link = %s WHERE ccode=%s and exam=%s",[uplink, course, etype])
			flash('Updated Successfully!!!', 'success')
		else:
			cur.execute("INSERT INTO drive(ccode, exam, link)VALUES(%s, %s, %s)", (course, etype, uplink))
			flash('Added Successfully!!!', 'success')
		mysql.connection.commit()
		cur.close()
		redirect(url_for('linkupdate'))
	return render_template('drivelink.html',form=form)
@app.route('/dashboard')
@is_logged_in
def dashboard():
	cur = mysql.connection.cursor()
	cur.execute("SELECT * FROM courses")
	tc = cur.fetchall()
	cur.execute("SELECT * FROM drive")
	td= cur.fetchall()
	return render_template('admin.html',tc=tc,td=td)
#===============================Logout====================================================

@app.route('/logout')
def logout():
	session.clear()
	flash('your logged out', 'success')
	return redirect(url_for('login'))


if __name__=='__main__':
	app.secret_key = 'some secret key'
	app.run()
