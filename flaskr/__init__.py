'''

This is the application facctory

This __init__.py serves double duty: it will contain the application
factory, and it tells Python that the flaskr directory should be 
treated as a package.

'''

import os,random

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # another simple page that says 2+3 =5
    @app.route('/add')
    def add():
        a = random.randint(0,9)
        b = random.randint(0,9)
        c = a + b
        myResponse = str(a) + " + " + str(b) + " = " + str(c)
        myList = ['a','b','c']
        myDict = {'key1':'value1','key2':'value2'}
        myResponse += "\nmyList: " +str(myList) + '\nmyDict: ' +\
                str(myDict)
        return myResponse

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    return app