from http.server import BaseHTTPRequestHandler, HTTPServer
from http import cookies
from urllib.parse import parse_qs
import json
import sys
from posts_db import PostsDB
from session_store import SessionStore
from passlib.hash import bcrypt

gSessionStore = SessionStore()

class MyRequestHandler(BaseHTTPRequestHandler):

    def end_headers(self):
        self.send_cookie()
        self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Access-Control-Allow-Origin", self.headers["Origin"])
        BaseHTTPRequestHandler.end_headers(self)
 
    def load_cookie(self):
        # create a cookie object and save into self.cookie
        if "Cookie" in self.headers:
            # read a header, capture the cookie
            self.cookie = cookies.SimpleCookie(self.headers["Cookie"])
        else:
            # or, create a cookie if one doesn't exist
            self.cookie = cookies.SimpleCookie()


    def send_cookie(self):
        for morsel in self.cookie.values():
            # write a header, sending cookie data (if any)
            self.send_header("Set-Cookie", morsel.OutputString())
        
    # using cookie data, load session data into self.sessionData
    def load_session_data(self):
        # first, load the cookie data
        self.load_cookie()
        # IF the sessionId is found in the cookie
        if "sessionId" in self.cookie:
            # load the session ID from the cookie
            sessionId = self.cookie["sessionId"].value
            # then, use the session ID to load the session data from the session store
            # save session data into variable for use later
            self.sessionData = gSessionStore.getSessionData(sessionId)
            # IF the session data DOES NOT exist in the session store
            if self.sessionData == None: # Server likely was restarted, data was lost
                # re-create the session and issue a new session ID into a cookie
                sessionId = gSessionStore.createSession()
                # save session data into variable for use later
                self.sessionData = gSessionStore.getSessionData(sessionId)
                # and create a new cookie value with the new session ID
                self.cookie["sessionId"] = sessionId
        # otherwise, IF no session ID in cookie
        else:
            # then, create a new sessino in the session store (createSession)
            sessionId = gSessionStore.createSession()
            # save session data into variable for use later
            self.sessionData = gSessionStore.getSessionData(sessionId)
            # and create a new cookie value with the new session ID
            self.cookie["sessionId"] = sessionId
            
            
    def handleSomeBadRequest(self, status_code):
        if status_code == 404:
            msg = "Path not found: " + self.path + " make sure your path is '/posts' for POST or GET requests, or '/posts/<id>' for UPDATE and DELETE requests."
        elif status_code == 400:
            msg = "Bad request syntax. You probably left one or more forms blank."
        elif status_code == 401:
            msg = "Authentication failure. Please log in and try again."
        elif status_code == 422:
            msg = "User already exists under that email."
        else:
            status_code = 500
            msg = "The server encountered an internal error and we're not sure why."
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(json.dumps(msg).encode("utf-8"))
        
    def handlePostRetrieveMember(self, post_id):
        # ENFORCE AUTHORIZATOIN (is user loggin in, or not?)
        if "userId" not in self.sessionData:
            self.handleSomeBadRequest(401)
            return
        db = PostsDB()
        post = db.getOnePost(post_id)
        if post:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(post), "utf-8"))
        else:
            self.handleSomeBadRequest(404)

    def handlePostRetrieveCollection(self):
        # ENFORCE AUTHORIZATOIN (is user loggin in, or not?)
        if "userId" not in self.sessionData:
            self.handleSomeBadRequest(401)
            return
        self.send_response(200)
        # headers go here
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        # body (data) goes here
        db = PostsDB()
        self.wfile.write(bytes(json.dumps(db.getAllPosts()), "utf-8"))


    def handlePostCreate(self):
        # ENFORCE AUTHORIZATOIN (is user loggin in, or not?)
        if "userId" not in self.sessionData:
            self.handleSomeBadRequest(401)
            return
        # capture data from the body and save it.
        # 1. read the raw data from the body
        length = self.headers["Content-Length"] # headers is a python dictionary
        body = self.rfile.read(int(length)).decode("utf-8")
        print("the RAW body: ", body)
        # 2. parse the raw data into usable data
        parsed_body = parse_qs(body)
        print("the PARSED body: ", parsed_body) # parsed_body is a python dictionary
        if len(parsed_body) < 5:
            self.handleSomeBadRequest(400)
            return
        # 3. if the data is good, save the data into the database
        fName = parsed_body["fName"][0]
        lName = parsed_body["lName"][0]
        message = parsed_body["message"][0]
        location = parsed_body["location"][0]
        date = parsed_body["date"][0]

        db = PostsDB()
        db.insertPost(fName,lName,message,location,date)
        #db.saveRecord({"name": name, "rating": rating, "hours": hours})
        self.send_response(201)
        self.end_headers()

    
    def handlePostDeleteMember(self,post_id):
        # ENFORCE AUTHORIZATOIN (is user loggin in, or not?)
        if "userId" not in self.sessionData:
            self.handleSomeBadRequest(401)
            return
        # 1. query the DB: get/load the Post by id
        db = PostsDB()
        post = db.getOnePost(post_id)
        # 2. if it exists? (!=None)>
        if post != None:
            # 3. delete the record from the DB
            db.deleteOnePost(post_id)
            # 4. respond to the client (200, no body)
            self.send_response(200)
            self.end_headers()
        else:
            self.handleSomeBadRequest(404)
            

    def handlePostUpdateMember(self, post_id):
        # ENFORCE AUTHORIZATOIN (is user loggin in, or not?)
        if "userId" not in self.sessionData:
            self.handleSomeBadRequest(401)
            return
        db = PostsDB()
        post = db.getOnePost(post_id)
        # 2. if it exists? (!=None)>
        print("Here is what db.GetOnePost returned: ", post)
        if post != None:
            length = self.headers["Content-Length"] # headers is a python dictionary
            body = self.rfile.read(int(length)).decode("utf-8")
            print("the RAW body: ", body)
            # 2. parse the raw data into usable data
            parsed_body = parse_qs(body)
            if len(parsed_body) < 5:
                self.handleSomeBadRequest(400)
                return
            print("the PARSED body: ", parsed_body) # parsed_body is a python dictionary
            # 3. if the data is valid, save the data into the database
            fName = parsed_body["fName"][0]
            lName = parsed_body["lName"][0]
            message = parsed_body["message"][0]
            location = parsed_body["location"][0]
            date = parsed_body["date"][0]
            # 3. delete the record from the DB
            db.updatePost(post_id, fName,lName,message,location,date)
            # 4. respond to the client (200, no body)
            self.send_response(200)
            self.end_headers()
        else:
            self.handleSomeBadRequest(404)
    
    
    def handleUserCreate(self):
        # read all data from the body, firstname, lastname, email, password
        # 1. read the raw data from the body
        length = self.headers["Content-Length"] # headers is a python dictionary
        body = self.rfile.read(int(length)).decode("utf-8")
        # 2. parse the raw data into usable data
        parsed_body = parse_qs(body)
        if len(parsed_body) < 4:
            self.handleSomeBadRequest(400)
            return
        # FIRST, check to see if the user exists in the DB
        db = PostsDB()
        user = db.getOneUserByEmail(parsed_body["email"][0])
        if user == None:
            # insert the new user into the DB
            firstName = parsed_body["firstName"][0]
            lastName = parsed_body["lastName"][0]
            email = parsed_body["email"][0]
            encryptedPassword = bcrypt.hash(parsed_body["password"][0])
            db.createNewUser(firstName, lastName, email, encryptedPassword)
            # success: 201
            self.send_response(201)
            self.end_headers()
        else:
            # If it DOES exist in DB:
            # failure: 422
            self.handleSomeBadRequest(422)

    def handleSessionCreate(self):
        length = self.headers["Content-Length"] # headers is a python dictionary
        body = self.rfile.read(int(length)).decode("utf-8")
        parsed_body = parse_qs(body)
        if len(parsed_body) < 2:
            self.handleSomeBadRequest(400)
            return
        email = parsed_body["email"][0]
        password = parsed_body["password"][0]
        
        print("in handleSessionCreate")
        
        # FIRST, check to see if the user exists in the DB
        db = PostsDB()
        user = db.getOneUserByEmail(email)
        # if it DOES exist in the DB:
        if user:
            # compare given password (from body) to hashed password (from DB)
            # if password matches:
            if bcrypt.verify(password, user["encryptedpassword"]):
                # SAVE USER'S ID INTO SESSION DATA!!!
                self.sessionData["userId"] = user["id"]
                self.send_response(201)
                self.end_headers()
            else:
                self.handleSomeBadRequest(401)
        else:
            self.handleSomeBadRequest(401)

    
    def do_OPTIONS(self):
        self.load_session_data()
        self.send_response(200)
        self.send_header("Access-Control-Allow-Methods","OPTIONS, GET, POST, PUT, DELETE")
        self.send_header("Access-Control-Allow-Headers","Content-Type")
        self.end_headers()


    def do_GET(self):
        self.load_session_data()
        print("GET request received! Path is: " + self.path)

        path_parts = self.path.split("/")
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None

        if resource =="posts" and identifier == None:
            self.handlePostRetrieveCollection()
        elif resource == "posts" and identifier != None:
            self.handlePostRetrieveMember(identifier)
        else:
            self.handleSomeBadRequest(404)
        return
        

    def do_POST(self):
        self.load_session_data()
        print("POST request received! Path is: " + self.path)
        if self.path == "/posts":
            self.handlePostCreate()
        elif self.path == "/users":
            self.handleUserCreate()
        elif self.path == "/sessions":
            self.handleSessionCreate()
        else:
            self.handleSomeBadRequest(404)
            
            
    def do_DELETE(self):
        self.load_session_data()
        print("DELETE request received! Path is: " + self.path)
        # parse the path (resource & identifier)
        path_parts = self.path.split("/")
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None
        if resource =="posts" and identifier == None:
            self.handleSomeBadRequest(404)
        elif resource == "posts" and identifier != None:
            self.handlePostDeleteMember(identifier)
        else:
            self.handleSomeBadRequest(404)
            
            
    def do_PUT(self):
        self.load_session_data()
        print("PUT request received! Path is: " + self.path)
        path_parts = self.path.split("/")
        resource = path_parts[1]
        if len(path_parts) > 2:
            identifier = path_parts[2]
        else:
            identifier = None
        if resource =="posts" and identifier == None:
            self.handleSomeBadRequest(404)
        elif resource == "posts" and identifier != None:
            self.handlePostUpdateMember(identifier)
        else:
            self.handleSomeBadRequest(404)


def run():
    db = PostsDB()
    db.createPostsTable()
    db.createUsersTable()
    db = None # disconnect

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    listen = ("0.0.0.0", port)
    server = HTTPServer(listen, MyRequestHandler)

    print("Server listening on", "{}:{}".format(*listen))
    server.serve_forever()


run()
