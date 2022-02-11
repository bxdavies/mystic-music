from flask import render_template, session
from . import main

#########
# Index #
#########
@main.route('/')
def index():
    return render_template('index.html')


###########
# Contact #
###########
@main.route('/contact')
def contact():
    return render_template('contact.html')


########
# Get Started #
########
@main.route('/get-started')
def getStarted():
    return render_template('get-started.html')


#########
# About #
#########
@main.route('/about')
def about():
    return render_template('about.html')

