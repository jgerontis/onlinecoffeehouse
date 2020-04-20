import os
import psycopg2
import psycopg2.extras
import urllib.parse

class PostsDB:

    def __init__(self):
        urllib.parse.uses_netloc.append("postgres")
        url = urllib.parse.urlparse(os.environ["DATABASE_URL"])

        self.connection = psycopg2.connect(
            cursor_factory=psycopg2.extras.RealDictCursor,
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )

        self.cursor = self.connection.cursor()


    def __del__(self):
        self.connection.close()

    
    def createPostsTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, firstname TEXT, lastname TEXT, message TEXT, location TEXT, date TEXT)")
        self.connection.commit()
        
    def createUsersTable(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, firstname TEXT, lastname TEXT, email TEXT NOT NULL UNIQUE, encryptedpassword TEXT)")
        self.connection.commit()
    
    def insertPost(self, firstname, lastname, message, location, date):
        # insert record into the table
        data = [firstname, lastname, message, location, date]
        self.cursor.execute("INSERT INTO posts (firstname, lastname, message, location, date) VALUES (%s,%s,%s,%s,%s)",data)
        self.connection.commit()


    def getAllPosts(self):
        self.cursor.execute("SELECT * FROM posts")
        Posts = self.cursor.fetchall() # fetchall gives a list back with a dictionary inside of it
        return Posts


    def getOnePost(self, Post_id):
        data = [Post_id]
        self.cursor.execute("SELECT * FROM posts WHERE id = %s", data)
        return self.cursor.fetchone()
        
        
    def deleteOnePost(self, Post_id):
        data = [Post_id]
        self.cursor.execute("DELETE FROM posts WHERE id = %s", data)
        return self.connection.commit()
        
        
    def updatePost(self, Post_id, firstname, lastname, message, location, date):
        data = [firstname, lastname, message, location, date, Post_id]
        self.cursor.execute("UPDATE posts SET firstname = %s, lastname = %s, message = %s, location = %s, date = %s WHERE id = %s", data)
        return self.connection.commit()
        
        
    def createNewUser(self, firstname, lastname, email, encryptedpassword):
        data = [firstname, lastname, email, encryptedpassword]
        self.cursor.execute("INSERT INTO users (firstname, lastname, email, encryptedpassword) VALUES (%s,%s,%s,%s)",data)
        self.connection.commit()
        
        
    def getOneUserByEmail(self, email):
        data = [email]
        self.cursor.execute("SELECT * FROM users WHERE email = %s", data)
        return self.cursor.fetchone()
