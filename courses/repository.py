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


def list_courses_by_department(department_id: int):
    return fetch_all(
        """
        SELECT
            id,
            department_id,
            code,
            title_vi,
            title_en,
            credits,
            lecture_hours,
            practice_hours,
            self_study_hours,
            short_description,
            is_active
        FROM courses
        WHERE department_id = ?
        ORDER BY title_vi COLLATE NOCASE
        """,
        (department_id,),
    )


def get_course(course_id: int):
    return fetch_one(
        """
        SELECT
            c.id,
            c.code,
            c.title_vi,
            c.title_en,
            c.credits,
            c.lecture_hours,
            c.practice_hours,
            c.self_study_hours,
            c.short_description,
            c.is_active,
            sy.target_program,
            sy.level,
            sy.module_type,
            sy.grading_scale,
            sy.passing_score,
            sy.teaching_method,
            sy.learning_resource_overview,
            sy.office_hours,
            sy.policy_note,
            l.full_name AS primary_lecturer_name,
            l.title AS primary_lecturer_title,
            l.email AS primary_lecturer_email,
            l.phone AS primary_lecturer_phone
        FROM courses c
        LEFT JOIN syllabi sy ON sy.course_id = c.id
        LEFT JOIN course_lecturers cl ON cl.course_id = c.id AND cl.is_primary = 1
        LEFT JOIN lecturers l ON l.id = cl.lecturer_id
        WHERE c.id = ?
        """,
        (course_id,),
    )


def get_course_detail(course_id: int):
    return fetch_one(
        """
        SELECT
            c.id,
            c.department_id,
            c.code,
            c.title_vi,
            c.title_en,
            c.credits,
            c.lecture_hours,
            c.practice_hours,
            c.self_study_hours,
            c.short_description,
            c.is_active,
            d.id AS department_id,
            d.code AS department_code,
            d.name_vi AS department_name_vi,
            d.name_en AS department_name_en,
            s.id AS school_id,
            s.code AS school_code,
            s.name_vi AS school_name_vi,
            sy.id AS syllabus_id,
            sy.target_program,
            sy.level,
            sy.module_type,
            sy.grading_scale,
            sy.passing_score,
            sy.teaching_method,
            sy.learning_resource_overview,
            sy.office_hours,
            sy.policy_note
        FROM courses c
        INNER JOIN departments d ON d.id = c.department_id
        INNER JOIN schools s ON s.id = d.school_id
        LEFT JOIN syllabi sy ON sy.course_id = c.id
        WHERE c.id = ?
        """,
        (course_id,),
    )


def create_course(
    department_id: int,
    code: str,
    title_vi: str,
    title_en: str | None,
    credits: int,
    lecture_hours: int,
    practice_hours: int,
    self_study_hours: int,
    short_description: str | None,
    is_active: int,
):
    return execute(
        """
        INSERT INTO courses (
            department_id,
            code,
            title_vi,
            title_en,
            credits,
            lecture_hours,
            practice_hours,
            self_study_hours,
            short_description,
            is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
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
        ),
    )


def update_course(
    course_id: int,
    code: str,
    title_vi: str,
    title_en: str | None,
    credits: int,
    lecture_hours: int,
    practice_hours: int,
    self_study_hours: int,
    short_description: str | None,
    is_active: int,
):
    execute(
        """
        UPDATE courses
        SET
            code = ?,
            title_vi = ?,
            title_en = ?,
            credits = ?,
            lecture_hours = ?,
            practice_hours = ?,
            self_study_hours = ?,
            short_description = ?,
            is_active = ?
        WHERE id = ?
        """,
        (
            code,
            title_vi,
            title_en,
            credits,
            lecture_hours,
            practice_hours,
            self_study_hours,
            short_description,
            is_active,
            course_id,
        ),
    )


def delete_course(course_id: int):
    delete("DELETE FROM courses WHERE id = ?", (course_id,))


def upsert_syllabus(
    course_id: int,
    managed_department_id: int,
    target_program: str | None,
    level: str | None,
    module_type: str | None,
    grading_scale: str | None,
    passing_score: float | None,
    teaching_method: str | None,
    learning_resource_overview: str | None,
    office_hours: str | None,
    policy_note: str | None,
):
    existing = fetch_one("SELECT id FROM syllabi WHERE course_id = ?", (course_id,))

    if existing:
        execute(
            """
            UPDATE syllabi
            SET
                managed_department_id = ?,
                target_program = ?,
                level = ?,
                module_type = ?,
                grading_scale = ?,
                passing_score = ?,
                teaching_method = ?,
                learning_resource_overview = ?,
                office_hours = ?,
                policy_note = ?,
                updated_at = datetime('now')
            WHERE course_id = ?
            """,
            (
                managed_department_id,
                target_program,
                level,
                module_type,
                grading_scale,
                passing_score,
                teaching_method,
                learning_resource_overview,
                office_hours,
                policy_note,
                course_id,
            ),
        )
        return existing["id"]

    return execute(
        """
        INSERT INTO syllabi (
            course_id,
            managed_department_id,
            target_program,
            level,
            module_type,
            grading_scale,
            passing_score,
            teaching_method,
            learning_resource_overview,
            office_hours,
            policy_note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            course_id,
            managed_department_id,
            target_program,
            level,
            module_type,
            grading_scale,
            passing_score,
            teaching_method,
            learning_resource_overview,
            office_hours,
            policy_note,
        ),
    )


def _find_lecturer_by_email(email: str):
    return fetch_one("SELECT id FROM lecturers WHERE email = ?", (email,))


def _find_lecturer_by_name(full_name: str, department_id: int):
    return fetch_one(
        "SELECT id FROM lecturers WHERE full_name = ? AND department_id = ?",
        (full_name, department_id),
    )


def upsert_primary_lecturer(
    course_id: int,
    department_id: int,
    full_name: str | None,
    title: str | None,
    email: str | None,
    phone: str | None,
):
    if not full_name:
        delete("DELETE FROM course_lecturers WHERE course_id = ? AND is_primary = 1", (course_id,))
        return

    lecturer = _find_lecturer_by_email(email) if email else None
    if lecturer is None:
        lecturer = _find_lecturer_by_name(full_name, department_id)

    if lecturer:
        lecturer_id = lecturer["id"]
        execute(
            """
            UPDATE lecturers
            SET title = ?, email = ?, phone = ?, department_id = ?
            WHERE id = ?
            """,
            (title, email, phone, department_id, lecturer_id),
        )
    else:
        lecturer_id = execute(
            """
            INSERT INTO lecturers (department_id, full_name, title, email, phone)
            VALUES (?, ?, ?, ?, ?)
            """,
            (department_id, full_name, title, email, phone),
        )

    delete("DELETE FROM course_lecturers WHERE course_id = ? AND is_primary = 1", (course_id,))
    execute(
        """
        INSERT INTO course_lecturers (course_id, lecturer_id, role, is_primary)
        VALUES (?, ?, 'LECTURER', 1)
        """,
        (course_id, lecturer_id),
    )


def list_course_lecturers(course_id: int):
    return fetch_all(
        """
        SELECT
            l.id,
            l.full_name,
            l.title,
            l.email,
            l.phone,
            cl.role,
            cl.is_primary
        FROM course_lecturers cl
        INNER JOIN lecturers l ON l.id = cl.lecturer_id
        WHERE cl.course_id = ?
        ORDER BY cl.is_primary DESC, l.full_name COLLATE NOCASE
        """,
        (course_id,),
    )


def list_prerequisites(course_id: int):
    return fetch_all(
        """
        SELECT
            cp.id,
            cp.relation_type,
            cp.note,
            c2.code AS required_code,
            c2.title_vi AS required_title
        FROM course_prerequisites cp
        INNER JOIN courses c2 ON c2.id = cp.required_course_id
        WHERE cp.course_id = ?
        ORDER BY cp.relation_type, c2.code
        """,
        (course_id,),
    )


def list_objectives(course_id: int):
    return fetch_all(
        """
        SELECT
            so.id,
            so.objective_code,
            so.objective_type,
            so.description,
            so.order_no
        FROM syllabi sy
        INNER JOIN syllabus_objectives so ON so.syllabus_id = sy.id
        WHERE sy.course_id = ?
        ORDER BY so.order_no, so.id
        """,
        (course_id,),
    )


def list_learning_outcomes(course_id: int):
    return fetch_all(
        """
        SELECT
            lo.id,
            lo.clo_code,
            lo.domain,
            lo.bloom_level,
            lo.description,
            lo.order_no
        FROM syllabi sy
        INNER JOIN learning_outcomes lo ON lo.syllabus_id = sy.id
        WHERE sy.course_id = ?
        ORDER BY lo.order_no, lo.id
        """,
        (course_id,),
    )


def list_topics(course_id: int):
    return fetch_all(
        """
        SELECT
            ct.id,
            ct.week_no,
            ct.session_no,
            ct.topic_title,
            ct.topic_detail,
            ct.theory_hours,
            ct.practice_hours,
            ct.self_study_hours,
            ct.teaching_activity,
            ct.learning_activity,
            ct.order_no
        FROM syllabi sy
        INNER JOIN course_topics ct ON ct.syllabus_id = sy.id
        WHERE sy.course_id = ?
        ORDER BY ct.order_no, ct.id
        """,
        (course_id,),
    )


def list_assessments(course_id: int):
    return fetch_all(
        """
        SELECT
            a.id,
            a.component_code,
            a.component_name,
            a.weight_percent,
            a.assessment_method,
            a.duration_minutes,
            a.requirement,
            a.clo_mapping_note,
            a.order_no
        FROM syllabi sy
        INNER JOIN assessments a ON a.syllabus_id = sy.id
        WHERE sy.course_id = ?
        ORDER BY a.order_no, a.id
        """,
        (course_id,),
    )


def list_references(course_id: int):
    return fetch_all(
        """
        SELECT
            rm.id,
            rm.ref_type,
            rm.citation,
            rm.author,
            rm.publisher,
            rm.publish_year,
            rm.isbn,
            rm.url,
            rm.language,
            rm.order_no
        FROM syllabi sy
        INNER JOIN references_materials rm ON rm.syllabus_id = sy.id
        WHERE sy.course_id = ?
        ORDER BY rm.order_no, rm.id
        """,
        (course_id,),
    )


def is_integrity_error(error: Exception) -> bool:
    return isinstance(error, sqlite3.IntegrityError)