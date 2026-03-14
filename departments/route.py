from flask import flash, redirect, render_template, request, url_for

from departments.init import departments_bp
from departments.service import (
    create_department,
    delete_department,
    get_department,
    list_departments_by_school,
    update_department,
)
from schools.service import get_school


@departments_bp.route("/school/<int:school_id>")
def index(school_id: int):
    school = get_school(school_id)
    if school is None:
        flash("Khong tim thay truong.", "danger")
        return redirect(url_for("schools.index"))

    departments = list_departments_by_school(school_id)
    return render_template("departments/index.html", school=school, departments=departments)


@departments_bp.route("/create/<int:school_id>", methods=["GET", "POST"])
def create_department_view(school_id: int):
    school = get_school(school_id)
    if school is None:
        flash("Khong tim thay truong.", "danger")
        return redirect(url_for("schools.index"))

    if request.method == "POST":
        try:
            department_id = create_department(school_id, request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Them khoa thanh cong.", "success")
            return redirect(url_for("courses.index", department_id=department_id))

    return render_template("departments/department_form.html", department=None, school=school)


@departments_bp.route("/<int:department_id>/edit", methods=["GET", "POST"])
def edit_department_view(department_id: int):
    department = get_department(department_id)
    if department is None:
        flash("Khong tim thay khoa.", "danger")
        return redirect(url_for("schools.index"))

    school = get_school(department["school_id"])
    if request.method == "POST":
        try:
            update_department(department_id, request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
        else:
            flash("Cap nhat khoa thanh cong.", "success")
            return redirect(url_for("courses.index", department_id=department_id))

    return render_template("departments/department_form.html", department=department, school=school)


@departments_bp.route("/<int:department_id>/delete", methods=["POST"])
def delete_department_view(department_id: int):
    department = get_department(department_id)
    if department is None:
        flash("Khong tim thay khoa.", "danger")
        return redirect(url_for("schools.index"))

    try:
        delete_department(department_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("courses.index", department_id=department_id))

    flash("Da xoa khoa.", "success")
    return redirect(url_for("departments.index", school_id=department["school_id"]))