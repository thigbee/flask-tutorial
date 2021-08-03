'''

This is the application facctory

This __init__.py serves double duty: it will contain the application
factory, and it tells Python that the flaskr directory should be 
treated as a package

Unlike the auth blueprint, the blog blueprint does not have a url_prefix. So the 
index view will be at /, the create view at /create, and so on. The blog is the 
main feature of Flaskr, so it makes sense that the blog index will be the main index.

However, the endpoint for the index view defined below will be blog.index. Some 
of the authentication views referred to a plain index endpoint. app.add_url_rule() 
associates the endpoint name 'index' with the / url so that url_for('index') or url_
for('blog.index') will both work, generating the same / URL either way.

In another application you might give the blog blueprint a url_prefix and define a 
separate index view in the application factory, similar to the hello view. Then the 
index and blog.index endpoints and URLs would be different.

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


    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    
    return app