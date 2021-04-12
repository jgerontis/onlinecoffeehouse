# Online Coffee House

Made for my final project in CS 3200 for Dixie State University.
Basic online (now-offline) forum where users can create an account
and post about how they like their coffee.

## Resources

**Posts**

Attributes:

* first name (string)
* last name (string)
* message (string)
* location (string)
* date (string)

**Users**

Attributes:

* first name (string)
* last name (string)
* email (string)
* enctrypted password (string)

## Schema

```sql
CREATE TABLE posts (
id integer PRIMARY KEY,
firstName text,
lastName text,
message text,
location text,
date text
);
CREATE TABLE users(
id integer PRIMARY KEY,
firstName text,
lastName text,
email TEXT NOT NULL UNIQUE,
encryptedPassword TEXT NOT NULL
);
```

## REST Endpoints

Name                           | Method | Path
-------------------------------|--------|------------------
Retrieve post collection | GET    | /posts
Retrieve post member     | GET    | /posts/*\<id\>*
Create post member       | POST   | /posts
Update post member       | PUT    | /posts/*\<id\>*
Delete post member       | DELETE | /posts/*\<id\>*
Create user member       | POST   | /users
Create session member    | POST   | /sessions

## Password Hashing

Passwords are hashed using standard bcrypt.

```python3

from passlib import bcrypt

encryptedPassword = bcrypt.hash(password)
.
.
.
if bcrypt.verify(password, user["encryptedPassword"] : 
.
.
.

```


