from flask import render_template
from . import app
from .database import session, Entry, User
from flask import request, redirect, url_for, flash
from flask_login import login_user, login_required, current_user
from werkzeug.security import check_password_hash

PAGINATE_BY = 10

@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):

    try:
        limit = int(request.args.get('limit', PAGINATE_BY))
        if limit < 10:
            limit = PAGINATE_BY
        if limit > 100:
            limit = 100
    except ValueError:
        limit = PAGINATE_BY

    # Zero-indexed page
    page_index = page - 1

    count = session.query(Entry).count()

    start = page_index * limit
    end = start + limit

    total_pages = (count - 1) // limit + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
        entries=entries,
        has_next=has_next,
        has_prev=has_prev,
        page=page,
        total_pages=total_pages
    )

@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user
    )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<id>")
def view_entry(id):
    entryid = int(id) + 1
    entries = session.query(Entry)
    for entry in entries:
        if str(entry.id) == str(entryid):
            entry=entry
            break
    return render_template("view_entry.html", entry=entry)

@app.route("/entry/<id>/edit", methods=["GET"])
def edit_entry_get(id):
    entryid = int(id) + 1
    entries = session.query(Entry)
    for entry in entries:
        if str(entry.id) == str(entryid):
            entry=entry
            break
    return render_template("edit_entry.html", entry=entry)

@app.route("/entry/<id>/edit", methods=["POST"])
def edit_entry_post(id):
    entryid = int(id) + 1
    entries = session.query(Entry)
    for entry in entries:
        if str(entry.id) == str(entryid):
            entry=entry
            break
    entry.title = request.form["title"]
    entry.content = request.form["content"]
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<id>/confirm-delete", methods=["GET"])
def delete_entry_confirm(id):
    entryid = int(id) + 1
    entries = session.query(Entry)
    for entry in entries:
        if str(entry.id) == str(entryid):
            entry=entry
            break
    return render_template("delete_entry.html", entry=entry)

@app.route("/entry/<id>/delete", methods=["GET", "DELETE"])
def delete_entry_post(id):
    entryid = int(id) + 1
    entries = session.query(Entry)
    for entry in entries:
        if str(entry.id) == str(entryid):
            entry=entry
            break
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))
