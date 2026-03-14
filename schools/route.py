from flask import flash, redirect, render_template, request, url_for

from schools.init import schools_bp
from schools.service import (
	create_school,
	delete_school,
	get_school,
	list_schools,
	update_school,
)


@schools_bp.route("/")
def index():
	schools = list_schools()
	return render_template("schools/index.html", schools=schools)


@schools_bp.route("/create", methods=["GET", "POST"])
def create_school_view():
	if request.method == "POST":
		try:
			create_school(request.form)
		except ValueError as exc:
			flash(str(exc), "danger")
		else:
			flash("Them truong thanh cong.", "success")
			return redirect(url_for("schools.index"))

	return render_template("schools/school_form.html", school=None)


@schools_bp.route("/<int:school_id>/edit", methods=["GET", "POST"])
def edit_school_view(school_id: int):
	school = get_school(school_id)
	if school is None:
		flash("Khong tim thay truong.", "danger")
		return redirect(url_for("schools.index"))

	if request.method == "POST":
		try:
			update_school(school_id, request.form)
		except ValueError as exc:
			flash(str(exc), "danger")
		else:
			flash("Cap nhat truong thanh cong.", "success")
			return redirect(url_for("departments.index", school_id=school_id))

	return render_template("schools/school_form.html", school=school)


@schools_bp.route("/<int:school_id>/delete", methods=["POST"])
def delete_school_view(school_id: int):
	try:
		delete_school(school_id)
	except ValueError as exc:
		flash(str(exc), "danger")
		return redirect(url_for("schools.index"))

	flash("Da xoa truong.", "success")
	return redirect(url_for("schools.index"))
