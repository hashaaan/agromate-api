import json
######################################
from flask import Flask, request, jsonify
from yaml import load, dump
from datetime import datetime
try:
    from flask_restful import Api, Resource, reqparse
    from yaml import CLoader as Loader, CDumper as Dumper
    from flask_mysqldb import MySQL
    from flask_cors import CORS
except ImportError:
    from yaml import Loader, Dumper

# Init app
app = Flask(__name__)
# allow cross origin requests
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
# Load yaml config file
db = load(open('db.yaml'), Loader=Loader)
# Configure db
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
api = Api(app)

class Users(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users")
        rv = cur.fetchall()
        cur.close()
        return rv

class User(Resource):
    def get(self, user_id):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users where u_id=%d;" % user_id )
        rs = cur.fetchall()
        cur.close()
        return rs

# Login
login_args = reqparse.RequestParser()
login_args.add_argument("email", type=str, help="Email is reqired!", required=True)
login_args.add_argument("password", type=str, help="Password is reqired!", required=True)
login_args.add_argument("type", type=str, help="Type is reqired!", required=True)

class Login(Resource):
    def post(self):
        args = login_args.parse_args()
        cur = mysql.connection.cursor()
        u_type = args.type
        email = args.email
        passw_in = args.password
        stmt = "SELECT * FROM users WHERE email='%s';"
        if u_type == "admin":
            stmt = "SELECT * FROM admins WHERE email='%s';"
        cur.execute(stmt % email)
        rs = cur.fetchone()
        cur.close()
        if rs:
            password = rs['password']
            success = False
            jsonStr = json.dumps(rs, indent=1, sort_keys=True, default=str)
            user = json.loads(jsonStr)
            if passw_in == password:
                success = True
                return { "success": success, "user": user }
            else:
                return { "success": success, "message": "Invalid email address or password!" }, 400
        return {"success": False, "message": "Invalid email address or password!"}, 400

# Register
reg_args = reqparse.RequestParser()
reg_args.add_argument("name", type=str, help="Name is reqired!", required=True)
reg_args.add_argument("email", type=str, help="Email is reqired!", required=True)
reg_args.add_argument("password", type=str, help="Password is reqired!", required=True)
reg_args.add_argument("mobile", type=str, help="Mobile number is reqired!", required=True)

class Register(Resource):
    def post(self):
        args = reg_args.parse_args()
        cur = mysql.connection.cursor()
        name = args.name
        email = args.email
        password = args.password
        # check if user aleready exists
        stmt = "SELECT * FROM users WHERE email='%s';"
        cur.execute(stmt % email)
        rs = cur.fetchone()
        if rs:
            return { "success": False, "message": "User already exists!" }, 400
        # if not create user
        stmt = "INSERT INTO users(name, email, password) VALUES(%s, %s, %s);"
        data = (name, email, password)
        rs = cur.execute(stmt, data)
        mysql.connection.commit()
        cur.close()
        if rs > 0:
            return { "success": True, "data": args }
        return { "success": False, "message": "User not registered!" }, 400

# Conversations
conv_post_args = reqparse.RequestParser()
conv_post_args.add_argument("message", type=str, help="Message is reqired!", required=True)
conv_post_args.add_argument("admin_id", type=int, help="Admin is reqired!", required=True)
conv_post_args.add_argument("user_id", type=int, help="User is reqired!", required=True)
conv_post_args.add_argument("sender", type=str, help="Sender type is reqired!", required=True)

# Check if conversation exists
def convExists(args):
    cur = mysql.connection.cursor()
    u_id = args.user_id
    a_id = args.admin_id
    stmt = "SELECT * FROM conversation WHERE admin_id=%s AND user_id=%s;"
    data = (a_id, u_id)
    cur.execute(stmt, data)
    rs = cur.fetchall()
    if len(rs) > 0:
        return rs[0].get("c_id")
    return False

# Create new message
def createMessage(data):
    cur = mysql.connection.cursor()
    stmt = "INSERT INTO conversation_reply(message, sender, created_at, c_id) VALUES(%s, %s, %s, %s);"
    rs = cur.execute(stmt, data)
    mysql.connection.commit()
    cur.close()
    return rs

class Conversations(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        stmt = "SELECT * FROM conversation"
        cur.execute(stmt)
        rs = cur.fetchall()
        if len(rs) > 0:
            jsonStr = json.dumps(rs, indent=1, sort_keys=True, default=str)
            return json.loads(jsonStr)
        return { "success": False, "message": "No conversations available!" }, 400

    def post(self):
        args = conv_post_args.parse_args()
        cur = mysql.connection.cursor()
        u_id = args.user_id
        a_id = args.admin_id
        sender = args.sender
        message = args.message
        c_time = datetime.now()
        exists = convExists(args)
        if not exists:
            stmt = "INSERT INTO conversation(admin_id, user_id, created_at, status) VALUES(%s, %s, %s, %s);"
            data = (a_id, u_id, c_time, 1)
            rs = cur.execute(stmt, data)
            mysql.connection.commit()
            cur.close()
            if rs > 0:
                conv_id = cur.lastrowid
                data = (message, sender, c_time, conv_id)
                createMessage(data)
        else:
            conv_id = exists
            data = (message, sender, c_time, conv_id)
            createMessage(data)
        
        return { "success": True, "data": args }, 201

class AdminConvo(Resource):
    def get(self, admin_id):
        cur = mysql.connection.cursor()
        stmt = "SELECT \
          conversation.c_id, \
          conversation.admin_id, \
          conversation.user_id, \
          conversation.created_at, \
          conversation.status, \
          users.name AS user_name \
          FROM conversation \
          INNER JOIN users ON users.u_id = conversation.user_id WHERE conversation.admin_id=%d;"
        cur.execute(stmt % admin_id)
        rs = cur.fetchall()
        cur.close()
        if len(rs) > 0:
            jsonStr = json.dumps(rs, indent=1, sort_keys=True, default=str)
            return json.loads(jsonStr)
        return { "success": False, "message": "No conversations available!" }, 400

class UserConvo(Resource):
    def get(self, user_id):
        cur = mysql.connection.cursor()
        stmt = "SELECT \
          conversation.c_id, \
          conversation.admin_id, \
          conversation.user_id, \
          conversation.created_at, \
          conversation.status, \
          admins.name AS admin_name, \
          admins.role AS admin_role \
          FROM conversation \
          INNER JOIN admins ON admins.a_id = conversation.admin_id WHERE conversation.user_id=%d;"
        cur.execute(stmt % user_id)
        rs = cur.fetchall()
        cur.close()
        if len(rs) > 0:
            jsonStr = json.dumps(rs, indent=1, sort_keys=True, default=str)
            return json.loads(jsonStr)
        return { "success": False, "message": "No conversations available!" }, 400

class Messages(Resource):
    def get(self, c_id):
        cur = mysql.connection.cursor()
        stmt = "SELECT * from conversation_reply WHERE c_id=%d;"
        cur.execute(stmt % c_id)
        rs = cur.fetchall()
        cur.close()
        if len(rs) > 0:
            jsonStr = json.dumps(rs, indent=1, sort_keys=True, default=str)
            return json.loads(jsonStr)
        return { "success": False, "message": "No messages available!" }, 400

# Define API routes
api.add_resource(Users, "/api/v1/users/")
api.add_resource(User, "/api/v1/users/<int:user_id>")
api.add_resource(Conversations, "/api/v1/conversations")
api.add_resource(AdminConvo, "/api/v1/conversations/admin/<int:admin_id>")
api.add_resource(UserConvo, "/api/v1/conversations/user/<int:user_id>")
api.add_resource(Messages, "/api/v1/messages/<int:c_id>")
# Auth routes
api.add_resource(Login, "/api/v1/auth/login")
api.add_resource(Register, "/api/v1/auth/register")

# Define index route
@app.route('/')
def index():
    return "<h1 align='center' style='color: green; margin-top: 100px'>Agromate API</h1>"

# Run server
if __name__ == '__main__':
    app.run(debug=True)