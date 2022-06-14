import sqlite3
from flask import g
from flask import Flask
from flask import request
from db_queries import sql
import argparse
from error_messages import lookup

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
        return {
            "success": True,
            "message": "Success!"
            }
    except sqlite3.IntegrityError as e:
        if str(e) in lookup:
            message = lookup[str(e)]
        else:
            message = str(e)
            print(str(e))
        return {
            "success": False,
            "message": message
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
    # name = request.args.get('name').lower()
    # password_hash = request.args.get('password_hash')
    name = request.headers.get('name').lower()
    password_hash = request.headers.get('password_hash')


    if name is None or password_hash is None or not name.isalnum() or not password_hash.isalnum():
        return {
            "success": False,
            "message": "Something was wrong with your credentials. Please try again"
        }

    if len(name) < 4:
        return {
            "success": False,
            "message": "Nickname doesn't exist"
        }

    query = sql.get("authenticate_user").replace("${name}", name).replace("${password_hash}", password_hash)
    data = query_db(query)
    if data[0]["name"] is None:
        message = "Incorrect account and password combination"
    else:
        message = "Login Successful"

    return {
        "success": bool(data[0]["success"]),
        "message": message,
        "name": name
    }


@app.route('/register')
def register():
    # name = request.args.get('name').lower()
    # password_hash = request.args.get('password_hash')
    name = request.headers.get('name').lower()
    password_hash = request.headers.get('password_hash')

    if name is None or password_hash is None:
        return {
            "success": False,
            "message": "Failed: Name and password cannot be blank"
        }

    if len(name) < 4:
        return {
            "success": False,
            "message": "Failed: Name must be at least four characters"
        }

    if not name.isalnum() or not password_hash.isalnum():
        return {
            "success": False,
            "message": "Failed: Name and password must be alphanumeric"
        }

    query = sql.get("register_user").replace("${name}", name).replace("${password_hash}", password_hash)
    data = insert_db(query)
    data["name"] = name
    return data

@app.route('/get_character_data')
def getCharacterData():
    name = request.headers.get('name').lower()
    query = sql.get("get_character_data").replace("${name}", name)
    data = query_db(query)

    if len(data) == 0:
        message = "Character does not exist"
        code = -1
    elif data[0]["character_creation_data"] is None:
        message = "No character data found. Starting to character creation."
        code = 0
    else:
        message = "Data found. Loading into game"
        code = 1

    return {
        "message": message,
        "name": name,
        "data": data[0]["character_creation_data"],
        "code": code

    }

@app.route('/set_character_data')
def setCharacterData():
    name = request.headers.get('name').lower()
    character_data = request.headers.get('character_data')
    query = sql.get("set_character_data").replace("${name}", name).replace("${character_data}", character_data)
    print(query)
    data = insert_db(query)

    return {
        "code": 0,
        "data": str(data)
    }



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Starts authentication server for metamochihorrorhouse')
    parser.add_argument('--host', default="127.0.0.1", type=str, help='host ip. typically 127.0.0.1 or 0.0.0.0')
    parser.add_argument('--port', default=7777, type=str, help='port to host server on')
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, ssl_context='adhoc')

