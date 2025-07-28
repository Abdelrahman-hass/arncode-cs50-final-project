from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from arnhub.models import Course, User, AdminRequest
from arnhub.decorators import admin_required
from arnhub import db
from datetime import datetime, timedelta

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/courses")
@login_required
def courses():
    # Show only published courses for normal users
    if current_user.is_authenticated and not current_user.is_admin:
        all_courses = Course.query.filter_by(is_published=True).all()
    else:
        all_courses = Course.query.all()
    
    your_courses = [c for c in all_courses if c.creator_id == current_user.id]
    team_courses = [c for c in all_courses if c.creator_id != current_user.id]
    
    return render_template("courses.html", your_courses=your_courses, team_courses=team_courses)

@main.route("/course/<int:course_id>")
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)

    if not course.is_published and not current_user.is_admin:
        abort(404)

    # Show only published lessons unless admin
    lessons = [
        l for l in course.lessons 
        if l.is_published or current_user.is_admin
    ]
    
    return render_template("course_detail.html", course=course, lessons=lessons)

@main.route("/course/<int:course_id>/lesson/<int:lesson_id>")
@login_required
def view_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = next((l for l in course.lessons if l.id == lesson_id), None)

    if not lesson or (not lesson.is_published and not current_user.is_admin):
        flash("Lesson not found or unpublished.", "danger")
        return redirect(url_for("main.course_detail", course_id=course_id))

    return render_template("view_lesson.html", course=course, lesson=lesson)

# 🔹 Admin Dashboard
@main.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin/dashboard.html")

@main.route("/admin/delete_course/<int:course_id>", methods=["POST"])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash("Course deleted successfully!", "success")
    return redirect(url_for("main.admin_dashboard"))

# 🔹 Request Admin Access
@main.route("/request-admin", methods=["GET", "POST"])
@login_required
def request_admin():
    if current_user.is_admin:
        flash("You are already an admin.", "info")
        return redirect(url_for("main.index"))

    existing = AdminRequest.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        reason = request.form.get("reason") 

        if existing:
            if existing.status in ["rejected", "revoked"]:
                existing.status = "pending"
                existing.comment = None
                existing.reason = reason  
                existing.timestamp = datetime.utcnow()
                db.session.commit()
                flash("Re-submitted admin request. Head admin will review again.", "success")
            else:
                flash("You already submitted a request.", "warning")
        else:
            new_req = AdminRequest(
                user_id=current_user.id,
                reason=reason, 
                status="pending",
                timestamp=datetime.utcnow()
            )
            db.session.add(new_req)
            db.session.commit()
            flash("Admin request submitted successfully.", "success")

        return redirect(url_for("main.request_admin")) 

    return render_template("request_admin.html", existing_request=existing)