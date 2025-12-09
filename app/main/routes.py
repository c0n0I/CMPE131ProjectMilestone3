from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from . import main_bp
from app.forms import BookmarkForm, FolderForm, CourseForm, AssignmentForm
from app.models import Bookmark, Folder, Course, Assignment, db

from app.models import Bookmark, Folder
from flask import request

@main_bp.route("/")
def index():
    return render_template("main/index.html")

@main_bp.route("/feature")
def feature():
    return render_template("main/feature.html")

@main_bp.route("/bookmarks")
@login_required
def bookmarks():
    user_folders = Folder.query.filter_by(user_id=current_user.id).all()

    user_bookmarks = Bookmark.query.filter_by(user_id=current_user.id).all()

    unfiled_bookmarks = [bm for bm in user_bookmarks if bm.folder_id is None]

    return render_template(
        "main/bookmarks.html",
        folders=user_folders,
        unfiled_bookmarks=unfiled_bookmarks
    )


@main_bp.route("/bookmarks/add", methods=["GET", "POST"])
@login_required
def add_bookmark():
    form = BookmarkForm()
    folders = Folder.query.filter_by(user_id=current_user.id).all()

    if form.validate_on_submit():
        selected_folder = request.form.get("folder_id")
        folder_id = int(selected_folder) if selected_folder else None

        new_bm = Bookmark(
            title=form.title.data,
            url=form.url.data,
            user_id=current_user.id,
            folder_id=folder_id
        )
        db.session.add(new_bm)
        db.session.commit()
        flash("Bookmark added!", "success")
        return redirect(url_for("main.bookmarks"))

    return render_template("main/add_bookmark.html", form=form, folders=folders)



@main_bp.route("/bookmarks/edit/<int:bookmark_id>", methods=["GET", "POST"])
@login_required
def edit_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)

    if bookmark.user_id != current_user.id:
        flash("You cannot edit another user's bookmark.", "danger")
        return redirect(url_for("main.bookmarks"))

    form = BookmarkForm(obj=bookmark)

    if form.validate_on_submit():
        bookmark.title = form.title.data
        bookmark.url = form.url.data
        db.session.commit()
        flash("Bookmark updated successfully!", "success")
        return redirect(url_for("main.bookmarks"))
    else:
        if form.is_submitted():
            flash("Please correct the errors in the form.", "danger")

    return render_template("main/edit_bookmark.html", form=form)

@main_bp.route("/bookmarks/delete/<int:bookmark_id>", methods=["POST"])
@login_required
def delete_bookmark(bookmark_id):
    bookmark = Bookmark.query.get_or_404(bookmark_id)

    if bookmark.user_id != current_user.id:
        flash("You cannot delete another user's bookmark.", "danger")
        return redirect(url_for("main.bookmarks"))

    db.session.delete(bookmark)
    db.session.commit()
    flash("Bookmark deleted successfully!", "success")
    return redirect(url_for("main.bookmarks"))

@main_bp.route("/folders")
@login_required
def folders():
    user_folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template("main/folders.html", folders=user_folders)


@main_bp.route("/folders/add", methods=["GET", "POST"])
@login_required
def add_folder():
    form = FolderForm()
    if form.validate_on_submit():
        new_folder = Folder(
            name=form.name.data,
            user_id=current_user.id
        )
        db.session.add(new_folder)
        db.session.commit()
        flash("Folder created successfully!", "success")
        return redirect(url_for("main.folders"))

    return render_template("main/add_folder.html", form=form)

@main_bp.route("/folders/delete/<int:folder_id>", methods=["POST"])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.get_or_404(folder_id)

    if folder.user_id != current_user.id:
        flash("You cannot delete another user's folder.", "danger")
        return redirect(url_for('main.folders'))

    db.session.delete(folder)
    db.session.commit()

    flash("Folder deleted successfully!", "success")
    return redirect(url_for('main.folders'))

@main_bp.route("/courses")
@login_required
def courses():
    all_courses = Course.query.all()
    return render_template("main/courses.html", courses=all_courses)

@main_bp.route("/courses/new", methods=["GET", "POST"])
@login_required
def new_course():
    if current_user.role != "instructor":
        flash("Only instructors can create courses.", "danger")
        return redirect(url_for("main.courses"))

    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash("Course created.", "success")
        return redirect(url_for("main.course_detail", course_id=course.id))
    return render_template("main/new_course.html", form=form)

@main_bp.route("/courses/<int:course_id>")
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    assignments = Assignment.query.filter_by(course_id=course.id).all()
    return render_template(
        "main/course_detail.html",
        course=course,
        assignments=assignments
    )

@main_bp.route("/courses/<int:course_id>/assignments/new", methods=["GET", "POST"])
@login_required
def new_assignment(course_id):
    course = Course.query.get_or_404(course_id)

    if current_user.role != "instructor" or course.instructor_id != current_user.id:
        flash("Only the course instructor can modify assignments.", "danger")
        return redirect(url_for("main.course_detail", course_id=course.id))

    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            course_id=course.id,
            title=form.title.data,
            description=form.description.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created!", "success")
        return redirect(url_for("main.course_detail", course_id=course.id))
    return render_template("main/new_assignment.html", form=form, course=course)

@main_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)

    if current_user.role != "instructor" or course.instructor_id != current_user.id:
        flash("Only the course instructor can delete this course.", "danger")
        return redirect(url_for("main.course_detail", course_id=course.id))

    db.session.delete(course)
    db.session.commit()
    flash("Course deleted.", "success")
    return redirect(url_for("main.courses"))

@main_bp.route("/assignments/<int:assignment_id>/delete", methods=["POST"])
@login_required
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    course = assignment.course

    if current_user.role != "instructor" or course.instructor_id != current_user.id:
        flash("Only the course instructor can delete assignments.", "danger")
        return redirect(url_for("main.course_detail", course_id=course.id))

    db.session.delete(assignment)
    db.session.commit()
    flash("Assignment deleted.", "success")
    return redirect(url_for("main.course_detail", course_id=course.id))