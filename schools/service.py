from collections.abc import Mapping

from schools import repository


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


def list_schools():
    return repository.list_schools()


def get_school(school_id: int | None):
    if not school_id:
        return None
    return repository.get_school(school_id)


def create_school(form: Mapping[str, str]) -> int:
    code = _require_text(form.get("code"), "Ma truong")
    name_vi = _require_text(form.get("name_vi"), "Ten truong")
    name_en = _optional_text(form.get("name_en"))

    try:
        return repository.create_school(code, name_vi, name_en)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Ma truong da ton tai.") from exc
        raise


def update_school(school_id: int, form: Mapping[str, str]) -> None:
    if repository.get_school(school_id) is None:
        raise ValueError("Khong tim thay truong.")

    code = _require_text(form.get("code"), "Ma truong")
    name_vi = _require_text(form.get("name_vi"), "Ten truong")
    name_en = _optional_text(form.get("name_en"))

    try:
        repository.update_school(school_id, code, name_vi, name_en)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Ma truong da ton tai.") from exc
        raise


def delete_school(school_id: int) -> None:
    if repository.get_school(school_id) is None:
        raise ValueError("Khong tim thay truong.")

    try:
        repository.delete_school(school_id)
    except Exception as exc:
        if repository.is_integrity_error(exc):
            raise ValueError("Khong the xoa truong vi van con khoa hoac du lieu lien quan.") from exc
        raise