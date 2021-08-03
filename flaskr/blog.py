'''

Blueprint for the actual 

Create:
The create view works the same as the auth register view. Either the form is 
displayed, or the posted data is validated and the post is added to the 
database or an error is shown.

The login_required decorator you wrote earlier is used on the blog views. A 
user must be logged in to visit these views, otherwise they will be redirected 
to the login page.

Update:
Both the update and delete views will need to fetch a post by id and check if 
the author matches the logged in user. To avoid duplicating code, you can 
write a function to get the post and call it from each view.

abort() will raise a special exception that returns an HTTP status 
code. It takes an optional message to show with the error, otherwise
a default message is used. 404 means “Not Found”, and 403 means 
“Forbidden”. (401 means “Unauthorized”, but you redirect to the 
login page instead of returning that status.)

The check_author argument is defined so that the function can be 
used to get a post without checking the author. This would be useful 
if you wrote a view to show an individual post on a page, where the 
user doesn’t matter because they’re not modifying the post.

Unlike the views you’ve written so far, the update function takes an argument, id. 
That corresponds to the <int:id> in the route. A real URL will look like /1/update. 
Flask will capture the 1, ensure it’s an int, and pass it as the id argument. If 
you don’t specify int: and instead do <id>, it will be a string. To generate a URL 
to the update page, url_for() needs to be passed the id so it knows what to fill 
in: url_for('blog.update', id=post['id']). This is also in the index.html file above.

The create and update views look very similar. The main difference is that the update 
view uses a post object and an UPDATE query instead of an INSERT. With some clever 
refactoring, you could use one view and template for both actions, but for the 
tutorial it’s clearer to keep them separate.

Delete:
The delete view doesn’t have its own template, the delete button is part of update.html 
and posts to the /<id>/delete URL. Since there is no template, it will only handle 
the POST method and then redirect to the index view.

'''


from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.
    Checks that the id exists and optionally that the current user is
    the author.
    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
