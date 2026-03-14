import sqlite3
from typing import Any

from database.init import get_db


def fetch_all(query: str, params: tuple[Any, ...] = ()):
    return get_db().execute(query, params).fetchall()


def fetch_one(query: str, params: tuple[Any, ...] = ()):
    return get_db().execute(query, params).fetchone()


def execute(query: str, params: tuple[Any, ...] = ()) -> int:
    db = get_db()
    cursor = db.execute(query, params)
    db.commit()
    return cursor.lastrowid


def delete(query: str, params: tuple[Any, ...] = ()) -> None:
    db = get_db()
    db.execute(query, params)
    db.commit()


def list_departments_by_school(school_id: int):
    return fetch_all(
        """
        SELECT
            d.id,
            d.school_id,
            d.code,
            d.name_vi,
            d.name_en,
            COUNT(c.id) AS course_count
        FROM departments d
        LEFT JOIN courses c ON c.department_id = d.id
        WHERE d.school_id = ?
        GROUP BY d.id, d.school_id, d.code, d.name_vi, d.name_en
        ORDER BY d.name_vi COLLATE NOCASE
        """,
        (school_id,),
    )


def get_department(department_id: int):
    return fetch_one(
        """
        SELECT
            d.id,
            d.school_id,
            d.code,
            d.name_vi,
            d.name_en,
            COUNT(c.id) AS course_count
        FROM departments d
        LEFT JOIN courses c ON c.department_id = d.id
        WHERE d.id = ?
        GROUP BY d.id, d.school_id, d.code, d.name_vi, d.name_en
        """,
        (department_id,),
    )


def create_department(school_id: int, code: str, name_vi: str, name_en: str | None):
    return execute(
        "INSERT INTO departments (school_id, code, name_vi, name_en) VALUES (?, ?, ?, ?)",
        (school_id, code, name_vi, name_en),
    )


def update_department(department_id: int, code: str, name_vi: str, name_en: str | None):
    execute(
        "UPDATE departments SET code = ?, name_vi = ?, name_en = ? WHERE id = ?",
        (code, name_vi, name_en, department_id),
    )


def delete_department(department_id: int):
    delete("DELETE FROM departments WHERE id = ?", (department_id,))


def is_integrity_error(error: Exception) -> bool:
    return isinstance(error, sqlite3.IntegrityError)