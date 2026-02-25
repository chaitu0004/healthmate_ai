import streamlit as st
import sqlite3

db_name="healthmate.db"
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    with sqlite3.connect(db_name) as conn:

        conn.execute("""
        create table if not exists users (
           userid INTEGER PRIMARY KEY AUTOINCREMENT,
           first_name TEXT NOT NULL,
           last_name TEXT NOT NULL,
           date_of_birth TEXT NOT NULL,
           email TEXT UNIQUE,
           password TEXT UNIQUE
        )

        """)


        conn.execute("""
        create table if not exists files (
           fileid INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id INTEGER NOT NULL,
           file_name TEXT NOT NULL,
           file_path TEXT NOT NULL,
           date_of_birth TEXT NOT NULL,
           FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        )

        """)

    print("database and tables insitialize")


def sign_up(first_name,lastname,date_of_birth,email,password):
    with sqlite3.connect(db_name) as conn:
        try:
            conn.connect("""
            
            insert into users (first_name,last_name,date_of_birth,email,password)
            values (?,?,?,?,?)
            """,(first_name,lastname,date_of_birth,email,hash_password(password)))
            conn.commit()

            return True,"account created succesfully,now you can login"

        except sqlite3.IntegrityError:
            return False,"this email already register,Try to login"

def login(email,password):

    with sqlite3.connect(db_name):
        user=conn.execute("""
        select * from users where email=?,password=? """,
        (email,hash_password(password))).fetchone()
        return user if user else None


def save_file(uesr_id,file_name,file_path):
    with sqlite3.connect(db_name) as conn:
        conn.execute("""
        insert into files(user_id,file_name,file_path)
        values(?,?,?)""",(uesr_id,file_name,file_path))
        conn.commit()


def get_file(user_id):
    with sqlite3.connect(db_name) as conn:
        files=conn.execute("""
        select file_name,file_path from files
        where user_id=?
        """,(user_id)).fetchall()
        return files

def delete_file(user_id,file_name):
    with sqlite3.connect(db_name) as conn:
        conn.execute("""
            delete from files where user_id=?,file_name=? """,
            (user_id,file_name)).fetchall()
        conn.commit()
        

init_db()      
        
        
        
        
        

