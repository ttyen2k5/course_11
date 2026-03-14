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


def list_schools():
    return fetch_all(
        """
        SELECT
            s.id,
            s.code,
            s.name_vi,
            s.name_en,
            COUNT(DISTINCT d.id) AS department_count,
            COUNT(DISTINCT c.id) AS course_count
        FROM schools s
        LEFT JOIN departments d ON d.school_id = s.id
        LEFT JOIN courses c ON c.department_id = d.id
        GROUP BY s.id, s.code, s.name_vi, s.name_en
        ORDER BY s.name_vi COLLATE NOCASE
        """
    )


def get_school(school_id: int):
    return fetch_one(
        """
        SELECT
            s.id,
            s.code,
            s.name_vi,
            s.name_en,
            COUNT(DISTINCT d.id) AS department_count,
            COUNT(DISTINCT c.id) AS course_count
        FROM schools s
        LEFT JOIN departments d ON d.school_id = s.id
        LEFT JOIN courses c ON c.department_id = d.id
        WHERE s.id = ?
        GROUP BY s.id, s.code, s.name_vi, s.name_en
        """,
        (school_id,),
    )


def create_school(code: str, name_vi: str, name_en: str | None):
    return execute(
        "INSERT INTO schools (code, name_vi, name_en) VALUES (?, ?, ?)",
        (code, name_vi, name_en),
    )


def update_school(school_id: int, code: str, name_vi: str, name_en: str | None):
    execute(
        "UPDATE schools SET code = ?, name_vi = ?, name_en = ? WHERE id = ?",
        (code, name_vi, name_en, school_id),
    )


def delete_school(school_id: int):
    delete("DELETE FROM schools WHERE id = ?", (school_id,))


def is_integrity_error(error: Exception) -> bool:
    return isinstance(error, sqlite3.IntegrityError)