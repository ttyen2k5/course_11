from collections.abc import Mapping

from courses import repository
from departments.repository import get_department


def _clean_text(value: str | None) -> str:
    return (value or "").strip()


def _optional_text(value: str | None) -> str | None:
    cleaned = _clean_text(value)
    return cleaned or None


def _require_text(value: str | None, field_name: str) -> str:
    cleaned = _clean_text(value)
    if not cleaned:
        raise ValueError(f"{field_name} la bat buoc.")
    return cleaned


def _parse_non_negative_int(value: str | None, field_name: str) -> int:
    raw_value = _clean_text(value) or "0"
    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{field_name} phai la so nguyen.") from exc

    if parsed < 0:
        raise ValueError(f"{field_name} khong duoc am.")
    return parsed


def _parse_non_negative_float(value: str | None, field_name: str) -> float | None:
    raw_value = _clean_text(value)
    if not raw_value:
        return None

    try:
        parsed = float(raw_value)
    except ValueError as exc:
        raise ValueError(f"{field_name} phai la so.") from exc

    if parsed < 0:
        raise ValueError(f"{field_name} khong duoc am.")
    return parsed


def _extract_syllabus_payload(form: Mapping[str, str], department_id: int) -> dict:
    return {
        "managed_department_id": department_id,
        "target_program": _optional_text(form.get("target_program")),
        "level": _optional_text(form.get("level")),
        "module_type": _optional_text(form.get("module_type")),
        "grading_scale": _optional_text(form.get("grading_scale")),
        "passing_score": _parse_non_negative_float(form.get("passing_score"), "Diem dat"),
        "teaching_method": _optional_text(form.get("teaching_method")),
        "learning_resource_overview": _optional_text(form.get("learning_resource_overview")),
        "office_hours": _optional_text(form.get("office_hours")),
        "policy_note": _optional_text(form.get("policy_note")),
    }


def _extract_primary_lecturer_payload(form: Mapping[str, str]) -> dict:
    return {
        "full_name": _optional_text(form.get("primary_lecturer_name")),
        "title": _optional_text(form.get("primary_lecturer_title")),
        "email": _optional_text(form.get("primary_lecturer_email")),
        "phone": _optional_text(form.get("primary_lecturer_phone")),
    }


def _save_course_extended_info(course_id: int, department_id: int, form: Mapping[str, str]) -> None:
    syllabus_payload = _extract_syllabus_payload(form, department_id)
    repository.upsert_syllabus(course_id, **syllabus_payload)

    lecturer_payload = _extract_primary_lecturer_payload(form)
    repository.upsert_primary_lecturer(course_id, department_id, **lecturer_payload)


def list_courses_by_department(department_id: int | None):
    if not department_id:
        return []
    return repository.list_courses_by_department(department_id)


def get_course(course_id: int | None):
    if not course_id:
        return None
    return repository.get_course(course_id)


def create_course(department_id: int, form: Mapping[str, str]) -> int:
    if get_department(department_id) is None:
        raise ValueError("Khong tim thay khoa.")

    code = _require_text(form.get("code"), "Ma mon hoc")
    title_vi = _require_text(form.get("title_vi"), "Ten mon hoc")
    title_en = _optional_text(form.get("title_en"))
    credits = _parse_non_negative_int(form.get("credits"), "So tin chi")
    lecture_hours = _parse_non_negative_int(form.get("lecture_hours"), "So gio ly thuyet")
    practice_hours = _parse_non_negative_int(form.get("practice_hours"), "So gio thuc hanh")
    self_study_hours = _parse_non_negative_int(form.get("self_study_hours"), "So gio tu hoc")
    short_description = _optional_text(form.get("short_description"))
    is_active = 1 if form.get("is_active") == "1" else 0

    try:
        course_id = repository.create_course(
            department_id,
            code,
            title_vi,
            title_en,
            credits,
            lecture_hours,
            practice_hours,
            self_study_hours,
            short_description,
            is_active,
        )
        _save_course_extended_info(course_id, department_id, form)
        return course_id
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Ma mon hoc da ton tai.") from exc
        raise


def update_course(course_id: int, form: Mapping[str, str]) -> None:
    course = repository.get_course(course_id)
    if course is None:
        raise ValueError("Khong tim thay mon hoc.")

    code = _require_text(form.get("code"), "Ma mon hoc")
    title_vi = _require_text(form.get("title_vi"), "Ten mon hoc")
    title_en = _optional_text(form.get("title_en"))
    credits = _parse_non_negative_int(form.get("credits"), "So tin chi")
    lecture_hours = _parse_non_negative_int(form.get("lecture_hours"), "So gio ly thuyet")
    practice_hours = _parse_non_negative_int(form.get("practice_hours"), "So gio thuc hanh")
    self_study_hours = _parse_non_negative_int(form.get("self_study_hours"), "So gio tu hoc")
    short_description = _optional_text(form.get("short_description"))
    is_active = 1 if form.get("is_active") == "1" else 0

    try:
        repository.update_course(
            course_id,
            code,
            title_vi,
            title_en,
            credits,
            lecture_hours,
            practice_hours,
            self_study_hours,
            short_description,
            is_active,
        )
        _save_course_extended_info(course_id, course["department_id"], form)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Ma mon hoc da ton tai.") from exc
        raise


def get_course_full(course_id: int):
    detail = repository.get_course_detail(course_id)
    if detail is None:
        return None

    return {
        "course": detail,
        "lecturers": repository.list_course_lecturers(course_id),
        "prerequisites": repository.list_prerequisites(course_id),
        "objectives": repository.list_objectives(course_id),
        "outcomes": repository.list_learning_outcomes(course_id),
        "topics": repository.list_topics(course_id),
        "assessments": repository.list_assessments(course_id),
        "references": repository.list_references(course_id),
    }


def delete_course(course_id: int) -> None:
    if repository.get_course(course_id) is None:
        raise ValueError("Khong tim thay mon hoc.")

    try:
        repository.delete_course(course_id)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Khong the xoa mon hoc vi van con du lieu lien quan.") from exc
        raise