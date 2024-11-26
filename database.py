import sqlite3


class SQL:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()

    def close_connection(self):
        return self.conn.close()

    def write_note(self, data):
        self.cur.execute("INSERT INTO notes VALUES(?, ?, ?);", data)
        self.conn.commit()

    def show_notes_by_date(self, date, user_id):
        return self.cur.execute("SELECT notedata FROM notes WHERE date == ? AND userid == ?",
                                (date, user_id,)).fetchall()

    def show_all_notes(self, user_id):
        return self.cur.execute("SELECT notedata, date FROM notes WHERE userid == ?", (user_id,)).fetchall()

    def remove_notes_by_date(self, date, user_id):
        self.cur.execute("DELETE FROM notes WHERE userid == ? AND date == ?", (user_id, date,))
        self.conn.commit()

    def remove_all_notes(self, user_id):
        self.cur.execute("DELETE FROM notes WHERE userid == ?", (user_id,))
        self.conn.commit()
