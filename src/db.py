import os

import psycopg2


# An abstraction of the database.
class Database:
    FETCH_NONE = 0
    FETCH_ONE = 1
    FETCH_ALL = 2

    def __init__(self, create_tables=False):
        # Configuration values are inherited from environment variables
        self.conn = psycopg2.connect(
            f"host={os.environ.get('POSTGRES_HOST', '127.0.0.1')} "
            f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
            f"password={os.environ.get('POSTGRES_PASSWORD', '')} "
            f"dbname={os.environ.get('POSTGRES_DB', 'postgres')} "
        )
        self.c = self.conn.cursor()
        if create_tables:
            self._create_tables()

    # Creates PostgreSQL tables
    def _create_tables(self):
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "   user_id INTEGER PRIMARY KEY NOT NULL,"
            "   first_name TEXT NOT NULL,"
            "   last_name TEXT,"
            "   username TEXT,"
            "   reputation INTEGER DEFAULT 0 NOT NULL,"
            "   warn_count INTEGER DEFAULT 0 NOT NULL,"
            "   banned BOOLEAN DEFAULT false NOT NULL,"
            "   permissions_level INTEGER DEFAULT 0 NOT NULL,"
            "   last_seen TIMESTAMP DEFAULT NOW() NOT NULL"
            ");"
        )
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS groups ("
            "   group_id INTEGER PRIMARY KEY NOT NULL,"
            "   title TEXT NOT NULL,"
            "   invite_link TEXT,"
            "   degree_name TEXT NOT NULL DEFAULT 'informatica',"
            "   academic_year INTEGER NOT NULL DEFAULT 0,"
            "   semester INTEGER NOT NULL DEFAULT 0"
            ");"
        )
        self.c.execute(
            "CREATE TABLE IF NOT EXISTS users_groups ("
            "   user_id INTEGER REFERENCES users(user_id),"
            "   group_id INTEGER REFERENCES groups(group_id)"
            ");"
        )
        self.conn.commit()

    def exec(self, *args, **kwargs):
        self.c.execute(*args)
        self.conn.commit()
        if kwargs.get("fetch", None) == Database.FETCH_ONE:
            return self.c.fetchone()
        elif kwargs.get("fetch") == Database.FETCH_ALL:
            return self.c.fetchall()

    # Updates (or inserts, if not exists) the user information in the database
    def update_user(self, user):
        db_user = self.exec("SELECT 1 FROM users WHERE user_id=%s", (user.id, ), fetch=Database.FETCH_ONE)
        if not db_user:
            self.exec(
                "INSERT INTO users(user_id, first_name, last_name, username, last_seen) "
                "VALUES (%s, %s, %s, %s, now());",
                (user.id, user.first_name, user.last_name, user.username, )
            )
        else:
            self.exec(
                "UPDATE users SET user_id=%s, first_name=%s, last_name=%s, username=%s, last_seen=NOW() "
                "WHERE user_id = %s",
                (user.id, user.first_name, user.last_name, user.username, user.id, )
            )
