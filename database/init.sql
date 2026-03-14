PRAGMA foreign_keys = ON;

-- BEGIN TRANSACTION;

-- 1) Don vi to chuc
CREATE TABLE IF NOT EXISTS schools (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	code TEXT NOT NULL UNIQUE,
	name_vi TEXT NOT NULL,
	name_en TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS departments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	school_id INTEGER NOT NULL,
	code TEXT NOT NULL,
	name_vi TEXT NOT NULL,
	name_en TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now')),
	UNIQUE (school_id, code),
	FOREIGN KEY (school_id) REFERENCES schools(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

-- 2) Chuong trinh dao tao
CREATE TABLE IF NOT EXISTS programs (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	school_id INTEGER NOT NULL,
	code TEXT NOT NULL UNIQUE,
	name_vi TEXT NOT NULL,
	name_en TEXT,
	degree_level TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now')),
	FOREIGN KEY (school_id) REFERENCES schools(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

-- 3) Mon hoc
CREATE TABLE IF NOT EXISTS courses (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	department_id INTEGER NOT NULL,
	code TEXT NOT NULL UNIQUE,
	title_vi TEXT NOT NULL,
	title_en TEXT,
	credits INTEGER NOT NULL DEFAULT 0 CHECK (credits >= 0),
	lecture_hours INTEGER NOT NULL DEFAULT 0 CHECK (lecture_hours >= 0),
	practice_hours INTEGER NOT NULL DEFAULT 0 CHECK (practice_hours >= 0),
	self_study_hours INTEGER NOT NULL DEFAULT 0 CHECK (self_study_hours >= 0),
	short_description TEXT,
	is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
	created_at TEXT NOT NULL DEFAULT (datetime('now')),
	FOREIGN KEY (department_id) REFERENCES departments(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

-- 4) De cuong mon hoc (tong quan)
CREATE TABLE IF NOT EXISTS syllabi (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	course_id INTEGER NOT NULL UNIQUE,
	managed_department_id INTEGER,
	target_program TEXT,
	level TEXT,
	module_type TEXT,
	grading_scale TEXT,
	passing_score REAL,
	teaching_method TEXT,
	learning_resource_overview TEXT,
	office_hours TEXT,
	policy_note TEXT,
	created_at TEXT NOT NULL DEFAULT (datetime('now')),
	updated_at TEXT NOT NULL DEFAULT (datetime('now')),
	FOREIGN KEY (course_id) REFERENCES courses(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (managed_department_id) REFERENCES departments(id)
		ON UPDATE CASCADE
		ON DELETE SET NULL
);

	-- 4.1) Giang vien va phan cong mon hoc
	CREATE TABLE IF NOT EXISTS lecturers (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		department_id INTEGER,
		full_name TEXT NOT NULL,
		title TEXT,
		email TEXT,
		phone TEXT,
		note TEXT,
		created_at TEXT NOT NULL DEFAULT (datetime('now')),
		UNIQUE (email),
		FOREIGN KEY (department_id) REFERENCES departments(id)
			ON UPDATE CASCADE
			ON DELETE SET NULL
	);

	CREATE TABLE IF NOT EXISTS course_lecturers (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		course_id INTEGER NOT NULL,
		lecturer_id INTEGER NOT NULL,
		role TEXT NOT NULL DEFAULT 'LECTURER',
		is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
		note TEXT,
		UNIQUE (course_id, lecturer_id, role),
		FOREIGN KEY (course_id) REFERENCES courses(id)
			ON UPDATE CASCADE
			ON DELETE CASCADE,
		FOREIGN KEY (lecturer_id) REFERENCES lecturers(id)
			ON UPDATE CASCADE
			ON DELETE CASCADE
	);

-- 5) Dieu kien hoc phan (tien quyet, song hanh, khuyen nghi...)
CREATE TABLE IF NOT EXISTS course_prerequisites (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	course_id INTEGER NOT NULL,
	required_course_id INTEGER NOT NULL,
	relation_type TEXT NOT NULL CHECK (
		relation_type IN ('PREREQUISITE', 'COREQUISITE', 'RECOMMENDED', 'REPLACED_BY')
	),
	note TEXT,
	UNIQUE (course_id, required_course_id, relation_type),
	FOREIGN KEY (course_id) REFERENCES courses(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (required_course_id) REFERENCES courses(id)
		ON UPDATE CASCADE
		ON DELETE RESTRICT
);

-- 6) Muc tieu mon hoc
CREATE TABLE IF NOT EXISTS syllabus_objectives (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	syllabus_id INTEGER NOT NULL,
	objective_code TEXT,
	objective_type TEXT CHECK (objective_type IN ('GENERAL', 'SPECIFIC')),
	description TEXT NOT NULL,
	order_no INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY (syllabus_id) REFERENCES syllabi(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 7) Chuan dau ra hoc phan (CLO)
CREATE TABLE IF NOT EXISTS learning_outcomes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	syllabus_id INTEGER NOT NULL,
	clo_code TEXT,
	domain TEXT CHECK (domain IN ('KNOWLEDGE', 'SKILL', 'ATTITUDE', 'OTHER')),
	bloom_level TEXT,
	description TEXT NOT NULL,
	order_no INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY (syllabus_id) REFERENCES syllabi(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 8) Noi dung giang day theo buoi/tuan/chuong
CREATE TABLE IF NOT EXISTS course_topics (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	syllabus_id INTEGER NOT NULL,
	week_no INTEGER,
	session_no INTEGER,
	topic_title TEXT NOT NULL,
	topic_detail TEXT,
	theory_hours REAL NOT NULL DEFAULT 0 CHECK (theory_hours >= 0),
	practice_hours REAL NOT NULL DEFAULT 0 CHECK (practice_hours >= 0),
	self_study_hours REAL NOT NULL DEFAULT 0 CHECK (self_study_hours >= 0),
	teaching_activity TEXT,
	learning_activity TEXT,
	order_no INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY (syllabus_id) REFERENCES syllabi(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 9) Danh gia hoc phan
CREATE TABLE IF NOT EXISTS assessments (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	syllabus_id INTEGER NOT NULL,
	component_code TEXT,
	component_name TEXT NOT NULL,
	weight_percent REAL NOT NULL DEFAULT 0 CHECK (weight_percent >= 0 AND weight_percent <= 100),
	assessment_method TEXT,
	duration_minutes INTEGER,
	requirement TEXT,
	clo_mapping_note TEXT,
	order_no INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY (syllabus_id) REFERENCES syllabi(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 10) Bang phu map thanh phan danh gia <-> chuan dau ra
CREATE TABLE IF NOT EXISTS assessment_outcome_map (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	assessment_id INTEGER NOT NULL,
	outcome_id INTEGER NOT NULL,
	coverage_level TEXT,
	UNIQUE (assessment_id, outcome_id),
	FOREIGN KEY (assessment_id) REFERENCES assessments(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (outcome_id) REFERENCES learning_outcomes(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 11) Tai lieu hoc tap va tham khao
CREATE TABLE IF NOT EXISTS references_materials (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	syllabus_id INTEGER NOT NULL,
	ref_type TEXT NOT NULL CHECK (ref_type IN ('REQUIRED', 'SUGGESTED', 'WEB', 'OTHER')),
	citation TEXT NOT NULL,
	author TEXT,
	publisher TEXT,
	publish_year INTEGER,
	isbn TEXT,
	url TEXT,
	language TEXT,
	order_no INTEGER NOT NULL DEFAULT 1,
	FOREIGN KEY (syllabus_id) REFERENCES syllabi(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 12) Anh xa mon hoc vao chuong trinh dao tao
CREATE TABLE IF NOT EXISTS program_courses (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	program_id INTEGER NOT NULL,
	course_id INTEGER NOT NULL,
	semester_no INTEGER CHECK (semester_no >= 1),
	is_mandatory INTEGER NOT NULL DEFAULT 1 CHECK (is_mandatory IN (0, 1)),
	note TEXT,
	UNIQUE (program_id, course_id),
	FOREIGN KEY (program_id) REFERENCES programs(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE,
	FOREIGN KEY (course_id) REFERENCES courses(id)
		ON UPDATE CASCADE
		ON DELETE CASCADE
);

-- 13) Chi muc ho tro truy van nhanh
CREATE INDEX IF NOT EXISTS idx_departments_school_id ON departments (school_id);
CREATE INDEX IF NOT EXISTS idx_courses_department_id ON courses (department_id);
CREATE INDEX IF NOT EXISTS idx_learning_outcomes_syllabus_id ON learning_outcomes (syllabus_id);
CREATE INDEX IF NOT EXISTS idx_topics_syllabus_id ON course_topics (syllabus_id);
CREATE INDEX IF NOT EXISTS idx_assessments_syllabus_id ON assessments (syllabus_id);
CREATE INDEX IF NOT EXISTS idx_references_syllabus_id ON references_materials (syllabus_id);
CREATE INDEX IF NOT EXISTS idx_lecturers_department_id ON lecturers (department_id);
CREATE INDEX IF NOT EXISTS idx_course_lecturers_course_id ON course_lecturers (course_id);

-- COMMIT;
