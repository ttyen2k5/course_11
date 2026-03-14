from flask import flash, redirect, render_template, request, url_for

from courses.init import courses_bp
from courses.service import (
    create_course,
    delete_course,
    get_course,
    get_course_full,
    list_courses_by_department,
    update_course,
)
from departments.service import get_department
from schools.service import get_school


@courses_bp.route("/department/<int:department_id>")
def index(department_id: int):
    department = get_department(department_id)
    if department is None:
        flash("Khong tim thay khoa.", "danger")
        return redirect(url_for("schools.index"))

    school = get_school(department["school_id"])
    courses = list_courses_by_department(department_id)
    return render_template("courses/index.html", school=school, department=department, courses=courses)


@courses_bp.route("/<int:course_id>")
def detail_course_view(course_id: int):
    detail = get_course_full(course_id)
    if detail is None:
        flash("Khong tim thay mon hoc.", "danger")
        return redirect(url_for("schools.index"))

    course = detail["course"]
    return render_template(
        "courses/detail.html",
        course=course,
        lecturers=detail["lecturers"],
        prerequisites=detail["prerequisites"],
        objectives=detail["objectives"],
        outcomes=detail["outcomes"],
        topics=detail["topics"],
        assessments=detail["assessments"],
        references=detail["references"],
    )


@courses_bp.route("/create/<int:department_id>", methods=["GET", "POST"])
def create_course_view(department_id: int):
    department = get_department(department_id)
    if department is None:
        flash("Khong tim thay khoa.", "danger")
        return redirect(url_for("schools.index"))

    if request.method == "POST":
        try:
            create_course(department_id, request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Them mon hoc thanh cong.", "success")
            return redirect(url_for("courses.index", department_id=department_id))

    return render_template("courses/course_form.html", course=None, department=department)


@courses_bp.route("/<int:course_id>/edit", methods=["GET", "POST"])
def edit_course_view(course_id: int):
    course = get_course(course_id)
    if course is None:
        flash("Khong tim thay mon hoc.", "danger")
        return redirect(url_for("schools.index"))

    department = get_department(course["department_id"])
    if request.method == "POST":
        try:
            update_course(course_id, request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Cap nhat mon hoc thanh cong.", "success")
            return redirect(url_for("courses.index", department_id=department["id"]))

    return render_template("courses/course_form.html", course=course, department=department)


@courses_bp.route("/<int:course_id>/delete", methods=["POST"])
def delete_course_view(course_id: int):
    course = get_course(course_id)
    if course is None:
        flash("Khong tim thay mon hoc.", "danger")
        return redirect(url_for("schools.index"))

    department = get_department(course["department_id"])
    try:
        delete_course(course_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("courses.index", department_id=department["id"]))

    flash("Da xoa mon hoc.", "success")
    return redirect(url_for("courses.index", department_id=department["id"]))