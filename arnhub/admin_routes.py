from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from arnhub.models import db, Course, Lesson, User, AdminRequest
from arnhub.decorators import admin_required
from arnhub.mail_config import mail
from flask_mail import Message
import os
from werkzeug.utils import secure_filename
import secrets
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from arnhub.mail_config import send_email
from arnhub.decorators import head_admin_required
from datetime import datetime
import json


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# --------------------------
# Admin Dashboard
# --------------------------
@admin_bp.route("/", endpoint="admin_dashboard")
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html")

# --------------------------
# Add New Course
# --------------------------
@admin_bp.route("/courses/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_course():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        category = request.form.get("category")
        difficulty = request.form.get("difficulty")
        duration = request.form.get("duration")
        is_published = bool(request.form.get("is_published"))

        course = Course(
            title=title,
            description=description,
            category=category,
            difficulty=difficulty,
            duration=duration,
            creator_id=current_user.id,
            is_published=is_published
        )
        db.session.add(course)
        db.session.commit()
        flash("Course created successfully!", "success")
        return redirect(url_for("admin.manage_courses"))

    return render_template("admin/create_edit_course.html", mode="add", course=None)

# --------------------------
# Edit Course
# --------------------------
@admin_bp.route("/courses/edit/<int:course_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == "POST":
        course.title = request.form["title"]
        course.description = request.form["description"]
        course.category = request.form.get("category")
        course.difficulty = request.form.get("difficulty")
        course.duration = request.form.get("duration")
        course.is_published = bool(request.form.get("is_published"))

        db.session.commit()
        flash("Course updated successfully!", "success")
        return redirect(url_for("admin.manage_courses"))

    return render_template("admin/create_edit_course.html", mode="edit", course=course)

# --------------------------
# Manage Courses
# --------------------------
@admin_bp.route("/courses")
@login_required
@admin_required
def manage_courses():
    if current_user.is_head_admin:
        courses = Course.query.all()
    else:
        courses = Course.query.filter_by(creator_id=current_user.id).all()
    return render_template("admin/manage_courses.html", courses=courses)

# --------------------------
# Delete Course
# --------------------------
@admin_bp.route("/courses/delete/<int:course_id>", methods=["POST"])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_head_admin and course.creator_id != current_user.id:
        flash("You are not allowed to delete this course.", "danger")
        return redirect(url_for("admin.manage_courses"))
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully!", "success")
    return redirect(url_for("admin.manage_courses"))

# --------------------------
# Lessons
# --------------------------
@admin_bp.route("/courses/<int:course_id>/lessons/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_lesson(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_head_admin and course.creator_id != current_user.id:
        flash("You are not allowed to add lessons to this course.", "danger")
        return redirect(url_for("admin.manage_courses"))

    if request.method == "POST":
        title = request.form["title"]
        is_published = bool(request.form.get("is_published"))

        # New: Parse JSON content sections
        sections_json = request.form.get("sections", "[]")
        try:
            sections = json.loads(sections_json)
        except Exception:
            flash("Invalid lesson content structure.", "danger")
            return redirect(request.url)

        # Handle video upload
        video = request.files.get("video")
        filename = None
        if video and video.filename:
            filename = secure_filename(video.filename)
            save_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
            video.save(save_path)

        lesson = Lesson(
            title=title,
            sections=sections,
            video_filename=filename,
            course_id=course_id,
            creator_id=current_user.id,
            is_published=is_published
        )
        db.session.add(lesson)
        db.session.commit()
        flash("Lesson added successfully!", "success")
        return redirect(url_for("admin.list_lessons", course_id=course_id))

    return render_template("admin/add_lesson.html", course=course)


@admin_bp.route("/courses/<int:course_id>/lessons")
@login_required
@admin_required
def list_lessons(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_head_admin and course.creator_id != current_user.id:
        flash("You are not allowed to view this course's lessons.", "danger")
        return redirect(url_for("admin.manage_courses"))
    return render_template("admin/lessons_list.html", course=course)


@admin_bp.route("/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(lesson.course_id)
    if not current_user.is_head_admin and course.creator_id != current_user.id:
        flash("You are not allowed to edit this lesson.", "danger")
        return redirect(url_for("admin.manage_courses"))

    if request.method == "POST":
        lesson.title = request.form["title"]
        lesson.is_published = bool(request.form.get("is_published"))

        # Updated: Parse new sections
        sections_json = request.form.get("sections_json", "[]")
        try:
            lesson.sections = json.loads(sections_json)
        except Exception:
            flash("Invalid section data.", "danger")
            return redirect(request.url)

        # Update video if a new one was uploaded
        video = request.files.get("video")
        if video and video.filename:
            filename = secure_filename(video.filename)
            save_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
            video.save(save_path)
            lesson.video_filename = filename

        db.session.commit()
        flash("Lesson updated successfully!", "success")
        return redirect(url_for("admin.list_lessons", course_id=course.id))

    return render_template("admin/edit_lesson.html", lesson=lesson)


@admin_bp.route("/lessons/<int:lesson_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    course = Course.query.get_or_404(lesson.course_id)
    if not current_user.is_head_admin and course.creator_id != current_user.id:
        flash("You are not allowed to delete this lesson.", "danger")
        return redirect(url_for("admin.manage_courses"))

    db.session.delete(lesson)
    db.session.commit()
    flash("Lesson deleted successfully!", "success")
    return redirect(url_for("admin.list_lessons", course_id=course.id))
# --------------------------
# Manage Users
# --------------------------
@admin_bp.route("/users")
@login_required
@admin_required
def users_list():
    if not current_user.is_head_admin:
        flash("Access denied. Head Admins only.", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    users = User.query.all()
    return render_template("admin/users.html", users=users)

@admin_bp.route("/users/edit/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def edit_user(user_id):
    if not current_user.is_head_admin:
        flash("Access denied. Head Admins only.", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    user = User.query.get_or_404(user_id)
    new_username = request.form.get("username")
    if new_username:
        user.username = new_username
        db.session.commit()
        flash("Username updated!", "success")
    return redirect(url_for("admin.users_list"))

@admin_bp.route("/users/reset-password/<int:user_id>", methods=["POST"])
@login_required
@admin_required
def reset_password(user_id):
    if not current_user.is_head_admin:
        flash("Access denied. Head Admins only.", "danger")
        return redirect(url_for("admin.admin_dashboard"))
    user = User.query.get_or_404(user_id)
    new_password = secrets.token_urlsafe(8)
    hashed_password = generate_password_hash(new_password)
    user.password = hashed_password
    db.session.commit()

    msg = Message("ARNcode Password Reset",
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email])
    msg.body = f"Hello {user.username},\n\nYour password has been reset.\n\nNew Password: {new_password}\n\nPlease login and change it.\n\nARNcode Team"
    try:
        mail.send(msg)
        flash("Password reset and email sent!", "success")
    except Exception:
        flash("Password reset, but failed to send email.", "warning")

    return redirect(url_for("admin.users_list"))

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    admin_request = AdminRequest.query.filter_by(user_id=user.id).first()
    if admin_request:
        db.session.delete(admin_request)

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users_list'))

# --------------------------
# Admin Requests
# --------------------------
@admin_bp.route("/request-admin", methods=["GET", "POST"])
@login_required
def request_admin():
    if current_user.is_admin:
        flash("You are already an admin.", "info")
        return redirect(url_for("main.index"))

    existing_request = AdminRequest.query.filter_by(user_id=current_user.id).first()

    # Allow resubmission if previous status was rejected or revoked
    if request.method == "POST":
        if existing_request and existing_request.status in ["pending", "approved"]:
            flash("You already submitted a request. Please wait for review.", "warning")
            return redirect(url_for("main.request_admin"))

        reason = request.form.get("reason", "").strip()
        if not reason:
            flash("Please explain why you want admin access.", "danger")
            return redirect(url_for("main.request_admin"))

        if existing_request and existing_request.status in ["rejected", "revoked"]:
            # Update the old request instead of making a new one
            existing_request.status = "pending"
            existing_request.comment = None
            existing_request.timestamp = datetime.utcnow()
            existing_request.reason = reason
            db.session.commit()
            flash("Request re-submitted successfully. Please wait for review.", "success")
        else:
            new_request = AdminRequest(
                user_id=current_user.id,
                reason=reason,
                timestamp=datetime.utcnow(),
                approved=False
            )
            db.session.add(new_request)
            db.session.commit()
            flash("Your request has been submitted successfully.", "success")

        return redirect(url_for("admin.request_admin"))

    return render_template("request_admin.html", existing_request=existing_request)

# --------------------------
# View Admin Requests
# --------------------------
@admin_bp.route("/admin-requests")
@login_required
@head_admin_required
def view_admin_requests():
    requests = AdminRequest.query \
        .filter(AdminRequest.status == "pending") \
        .order_by(AdminRequest.timestamp.desc()) \
        .all()
    return render_template("admin/admin_requests.html", requests=requests)

# -----------------------
# Approve Admin Request
# -----------------------
@admin_bp.route("/admin-requests/approve/<int:request_id>", methods=["POST"])
@login_required
@admin_required
def approve_admin_request(request_id):
    if not current_user.is_head_admin:
        flash("Access denied. Head Admins only.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    req = AdminRequest.query.get_or_404(request_id)
    user = User.query.get(req.user_id)

    user.is_admin = True
    user.is_head_admin = False

    req.approved = True
    req.status = "approved" 
    req.timestamp = datetime.utcnow()

    db.session.commit()
    flash(f"{user.username} is now an admin!", "success")
    return redirect(url_for("admin.view_admin_requests"))


@admin_bp.route("/reject-admin/<int:request_id>", methods=["POST"])
@head_admin_required
def reject_admin_request(request_id):
    reason = request.form.get("reason")
    request_obj = AdminRequest.query.get_or_404(request_id)
    request_obj.status = "rejected"
    request_obj.comment = reason
    db.session.commit()

    send_email(request_obj.user.email, "Admin Request Rejected", reason)

    flash("Request rejected and reason sent.", "info")
    return redirect(url_for("admin.view_admin_requests")) 


@admin_bp.route('/revoke-admin/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def revoke_admin(user_id):
    user = User.query.get_or_404(user_id)
    comment = request.form.get("comment", "").strip()

    if user.is_admin and not user.is_head_admin:
        user.is_admin = False

        # Update the AdminRequest status to 'revoked'
        request_record = AdminRequest.query.filter_by(user_id=user.id, status="approved").first()
        if request_record:
            request_record.status = "revoked"
            request_record.comment = comment
            request_record.timestamp = datetime.utcnow()

        db.session.commit()
        flash(f"Admin rights revoked for {user.username}.", "warning")
    else:
        flash("Cannot revoke head admin or non-admin user.", "danger")

    return redirect(url_for("admin.users_list"))