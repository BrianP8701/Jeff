from server.database.db import Database


if __name__ == "__main__":
    db = Database()
    db.clear_all_tables()
    db.reset_tables()
