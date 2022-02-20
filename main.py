import sqlite3
from flask import g
from flask import Flask
from flask import request
from db_queries import sql

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

DATABASE = 'metamochihorrorhouse-auth-database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

        def make_dicts(cursor, row):
            return dict((cursor.description[idx][0], value)
                        for idx, value in enumerate(row))

        db.row_factory = make_dicts

    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=(), one=False):
    try:
        con = get_db()
        cur = con.execute(query, args)
        con.commit()
        cur.close()
        return {"account_created": "true"}
    except sqlite3.IntegrityError as e:
        return {
            "account_created": "false",
            "message": str(e)
        }


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/users')
def index():
    data = query_db(sql.get("get_all_users"))
    # for user in data:
    #     print(user['name'], "has the password hash ", user["password_hash"])
    return {"users" : data}


@app.route('/authenticate')
def authenticate():
    name = request.args.get('name')
    password_hash = request.args.get('password_hash')

    if not name.isalnum() or not password_hash.isalnum():
        return {
            "error": "name or hash is not alphanumeric"
        }

    query = sql.get("authenticate_user").replace("${name}", name).replace("${password_hash}", password_hash)
    data = query_db(query)
    return data[0]

@app.route('/register')
def register():
    name = request.args.get('name')
    password_hash = request.args.get('password_hash')

    if not name.isalnum() or not password_hash.isalnum():
        return {
            "error": "name or hash is not alphanumeric"
        }

    query = sql.get("register_user").replace("${name}", name).replace("${password_hash}", password_hash)
    data = insert_db(query)
    return data


if __name__ == "__main__":
    app.run()