#diary.py which handles the functions for the diary
import mariadb
import sys
import os
from colorama import Fore, init, Style
import time
init(autoreset=True)

def sub_menu_diary(user_id, conn):
    while True:
        try:
            print(f"***Diary menu***\n",
                "1. Write a new entry\n",
                "2. Print an entry\n",
                "3. Go back\n")
            diary_menu_choice=int(input("Please make a choice: "))
            if diary_menu_choice == 1:
                new_entry(conn, user_id)
            elif diary_menu_choice == 2:
                show_entry(conn, user_id)
            elif diary_menu_choice == 3:
                print("Going back...")
                time.sleep(1)
                return
            else:
                print(Fore.RED + "Wrong input, please try again.")
        except ValueError:
            print(Fore.RED + "Only integers are allowed, try again.")

def new_entry(conn, user_id):
    cur=conn.cursor()
    entry_text = input("Enter your input-entry: ")
    cur.execute("INSERT INTO diary(content, user_id)VALUES(?, ?)", ([entry_text, user_id]))
    conn.commit()


def show_entry(conn, user_id):
    cur=conn.cursor()
    cur.execute("SELECT entry_date, content FROM diary WHERE user_id = (?) ORDER BY entry_date DESC LIMIT 20", (user_id,))
    rows = cur.fetchall()
    if rows:
        for i in rows:
            entry_date, content = i
            print(f"| {entry_date} | {content} |")
    else:
        print("No entries found...")
        return

def delete_entry(conn, user_id):
    show_entry()

def avail_diaries(conn, user_id):
    pass

#Test function
def checking(user_id):
    print(user_id)