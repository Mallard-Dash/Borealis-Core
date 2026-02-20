#diary.py which handles the functions for the diary
import main

def check_username(username):
    main.database_connection()
    cur=conn.cursor()
    try:
        cur.execute("SELECT * FROM users WHERE username = ?", (username))
        return username
    except mariadb.Error as e:
        return(f"Error: {e}")

def new_entry():
    main.database_connection()
    cur=conn.cursor()
    username=input("What is your name?")
    check_username()
    entry_text = input("Enter your input-entry: ")
    cur.execute("INSERT INTO diary"())


def show_entry():
    main.database_connection()

def delete_entry():
    main.database_connection()

def avail_diaries():
    main.database_connection()
