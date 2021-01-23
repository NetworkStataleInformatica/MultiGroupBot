CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT,
    username TEXT,
    reputation INTEGER DEFAULT 0 NOT NULL,
    warn_count INTEGER DEFAULT 0 NOT NULL,
    banned BOOLEAN DEFAULT false NOT NULL,
    permissions_level INTEGER DEFAULT 0 NOT NULL,
    last_seen TIMESTAMP DEFAULT NOW() NOT NULL
);

CREATE TYPE degree_type AS ENUM ('triennale', 'magistrale');
CREATE TABLE IF NOT EXISTS degrees (
    name TEXT,
    type degree_type,
    PRIMARY KEY (name, type)
);

CREATE TABLE IF NOT EXISTS groups (
    group_id BIGINT PRIMARY KEY NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    profile_picture BYTEA,
    invite_link TEXT,
    welcome_message TEXT
);

CREATE TABLE IF NOT EXISTS courses (
    course_id SERIAL NOT NULL PRIMARY KEY,
    group_id BIGINT REFERENCES groups(group_id) NOT NULL,
    name TEXT NOT NULL,
    cfu INTEGER NOT NULL,
    department TEXT,
    wiki_link TEXT
);

CREATE TABLE IF NOT EXISTS degrees_courses (
    degree_name TEXT,
    degree_type degree_type,
    group_id BIGINT REFERENCES courses(course_id),
    year INT NOT NULL,  -- for complementary courses, year is set to -1
    semester INT NOT NULL,
    FOREIGN KEY (degree_name, degree_type) REFERENCES degrees(name, type),
    PRIMARY KEY(degree_name, degree_type, group_id)
);

CREATE TABLE IF NOT EXISTS courses_links (
    course_id SERIAL REFERENCES courses(course_id) PRIMARY KEY,
    url TEXT NOT NULL,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users_groups (
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    group_id BIGINT REFERENCES groups(group_id) ON DELETE CASCADE,
    last_seen TIMESTAMP DEFAULT now(),
    PRIMARY KEY(user_id, group_id)
);

CREATE TABLE IF NOT EXISTS autodelete_messages (
    group_id BIGINT NOT NULL,
    message_id INT NOT NULL,
    delete_time TIMESTAMP,
    PRIMARY KEY(group_id, message_id)
);

CREATE TABLE IF NOT EXISTS administrators (
    user_id INTEGER PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    permissions_level INTEGER NOT NULL DEFAULT 0,
    departement TEXT NOT NULL
);
