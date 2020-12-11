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
            "   group_id BIGINT PRIMARY KEY NOT NULL,"
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
            "   group_id BIGINT REFERENCES groups(group_id),"
            "   last_seen TIMESTAMP DEFAULT now(),"
            "   PRIMARY KEY(user_id, group_id)"
            ");"
        )
        self.conn.commit()

    # Database cursor wrapper
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
                "UPDATE users SET first_name=%s, last_name=%s, username=%s, last_seen=NOW() "
                "WHERE user_id = %s",
                (user.first_name, user.last_name, user.username, user.id, )
            )

    # Updates the group information in the database
    # If the group is not in the database, it leaves
    def update_group(self, chat, user):
        db_group = self.exec("SELECT 1 FROM groups WHERE group_id=%s", (chat.id, ), fetch=Database.FETCH_ONE)
        if not db_group:
            chat.send(
                "@admin gruppo non registrato. "
                "Un amministratore deve registrarmi prima di aggiungermi a un gruppo. "
                "\n<b><u>Esco dalla chat</u></b>."
                f"\n\n(Chat ID: <code>{chat.id}</code>)", syntax="html"
            )
            return chat.leave()

        self.exec(
            "UPDATE groups SET title=%s",
            (chat.title, )
        )
        db_user_group = self.exec("SELECT 1 FROM users_groups WHERE user_id=%s AND group_id=%s",
                                  (user.id, chat.id, ),
                                  fetch=Database.FETCH_ONE)
        if not db_user_group:
            self.exec(
                "INSERT INTO users_groups(user_id, group_id) VALUES(%s, %s)",
                (user.id, chat.id, )
            )
        self.exec(
            "UPDATE users_groups SET last_seen=NOW() WHERE user_id=%s AND group_id=%s",
            (user.id, chat.id)
        )

    def get_rep(self, user):
        res = self.exec(
            "SELECT reputation FROM users WHERE user_id=%s LIMIT 1",
            (user.id, ),
            fetch=Database.FETCH_ONE
        )
        return -1 if not res else res[0]

    def increase_rep(self, user):
        self.exec("UPDATE users SET reputation=reputation+1 WHERE user_id=%s", (user.id, ))

    def get_permissions_level(self, user):
        res = self.exec(
            "SELECT permissions_level FROM users WHERE user_id=%s LIMIT 1",
            (user.id, ),
            fetch=Database.FETCH_ONE
        )
        return -1 if not res else res[0]
