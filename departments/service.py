from collections.abc import Mapping

from departments import repository
from schools.service import get_school


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


def list_departments_by_school(school_id: int | None):
    if not school_id:
        return []
    return repository.list_departments_by_school(school_id)


def get_department(department_id: int | None):
    if not department_id:
        return None
    return repository.get_department(department_id)


def create_department(school_id: int, form: Mapping[str, str]) -> int:
    if get_school(school_id) is None:
        raise ValueError("Khong tim thay truong.")

    code = _require_text(form.get("code"), "Ma khoa")
    name_vi = _require_text(form.get("name_vi"), "Ten khoa")
    name_en = _optional_text(form.get("name_en"))

    try:
        return repository.create_department(school_id, code, name_vi, name_en)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Ma khoa da ton tai trong truong nay.") from exc
        raise


def update_department(department_id: int, form: Mapping[str, str]) -> None:
    if repository.get_department(department_id) is None:
        raise ValueError("Khong tim thay khoa.")

    code = _require_text(form.get("code"), "Ma khoa")
    name_vi = _require_text(form.get("name_vi"), "Ten khoa")
    name_en = _optional_text(form.get("name_en"))

    try:
        repository.update_department(department_id, code, name_vi, name_en)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Ma khoa da ton tai trong truong nay.") from exc
        raise


def delete_department(department_id: int) -> None:
    if repository.get_department(department_id) is None:
        raise ValueError("Khong tim thay khoa.")

    try:
        repository.delete_department(department_id)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Khong the xoa khoa vi van con mon hoc hoac du lieu lien quan.") from exc
        raise