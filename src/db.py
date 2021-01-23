import os

import psycopg2


# An abstraction of the database.
class Database:
    FETCH_NONE = 0
    FETCH_ONE = 1
    FETCH_ALL = 2

    def __init__(self):
        # Configuration values are inherited from environment variables
        self.conn = psycopg2.connect(
            f"host={os.environ.get('POSTGRES_HOST', '127.0.0.1')} "
            f"user={os.environ.get('POSTGRES_USER', 'postgres')} "
            f"password={os.environ.get('POSTGRES_PASSWORD', '')} "
            f"dbname={os.environ.get('POSTGRES_DB', 'postgres')} "
        )
        self.c = self.conn.cursor()

    # Database cursor wrapper
    def exec(self, *args, **kwargs):
        self.c.execute(*args)
        self.conn.commit()
        if kwargs.get("fetch", None) == Database.FETCH_ONE:
            return self.c.fetchone()
        elif kwargs.get("fetch") == Database.FETCH_ALL:
            return self.c.fetchall()

    # Updates (or inserts, if not exists) the user information in the database
    def update_user(self, user, chat):
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
        group_exists = self.exec("SELECT EXISTS(SELECT 1 FROM groups WHERE group_id=%s)",
                                 (chat.id, ), fetch=Database.FETCH_ONE)
        if not group_exists:
            return
        self.exec("INSERT INTO users_groups(user_id, group_id, last_seen) VALUES(%s, %s, NOW()) "
                  "ON CONFLICT(user_id, group_id) DO UPDATE SET last_seen=NOW()", (user.id, chat.id, ))

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
