from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    db = get_db()
    posts = db.execute(
        "SELECT id, title, body, created, email, price"
        " FROM post"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


def get_post(id):
    """Get a post by id.

    :param id: id of post to get
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    """
    post = (
        get_db()
        .execute(
            "SELECT id, title, body, created, email, price"
            " FROM post"
            " WHERE id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    return post


@bp.route("/create", methods=("GET", "POST"))
def create():
    """Create a new post """
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        email = request.form["email"]
        price = request.form["price"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, email, price) VALUES (?, ?, ?, ?)",
                (title, body, email, price),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
def update(id):
    """Update a post."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        price = request.form["price"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?, email = ?, price = ? WHERE id = ?", 
                (title, body, email, price, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    """Delete a post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
