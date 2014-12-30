from flask import render_template
from flask.ext.user import login_required
from app import app

@app.route('/')
@app.route('/index')
@login_required
def index():
	return render_template('index.html')