#login.py
import mariadb
import os
from colorama import init, Fore, Style
init(autoreset=True)

conn = mariadb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host="127.0.0.1",
    port=int(os.getenv("DB_PORT")),
    database="healthlogger"
)

def new_user():
    cur=conn.cursor()
    while True:
        try:
            username=input("Please enter username: ")
            password=input("Now choose a good password with at least 4 characters: ")
            password2=input("Enter the same password again: ")

            if password != password2:
                print(Fore.RED + "Passwords do not match, please try again!")
                continue
            elif password == password2:
                try:
                    cur.execute("INSERT INTO users(username, passwd)VALUES(?, ?)", (username, password))
                    conn.commit()
                    print(Fore.GREEN + f"User {username} created!")
                    return
                except mariadb.IntegrityError:
                    print(Fore.RED + f"Username '{username}' is already taken, please choose another one")
                    continue
        except KeyboardInterrupt:
            print("\nReturning...")
            return

def authenticate():
    cur=conn.cursor()
    while True:
        try:
            username=input("Enter your username: ")
            password=input("Enter your password: ")
            cur.execute("SELECT user_id FROM users WHERE username = (?) AND passwd =(?)", [username, password])
            user_id= cur.fetchone()
            if user_id:
                print(Fore.GREEN + f"Logged in! Welcome back {username}")
                user_session = (user_id[0])
                return user_session
            elif user_id == None:
                print(Fore.RED + "Wrong password/username, try again!")
                return None
        except KeyboardInterrupt:
            print("\nReturning to menu")
            return None
        except mariadb.Error as e:
            print(Fore.RED + f"Error: {e}")
            continue



def login_menu():
    while True:
        try:
            print("***Login-menu***\n",
                "1. Login existing user\n",
                "2. Create new user\n",
                "3. Exit\n")
            first_choice=int(input("Welcome! Please pick a choice from 1-3: "))
            if first_choice == 1:
                session = authenticate()
                if session:
                    return session
            elif first_choice == 2:
                new_user()
            elif first_choice == 3:
                print("Good bye! :)")
                time.sleep(1)
                break
            else:
                print(Fore.YELLOW + "Please enter a valid choice!")
        except ValueError:
            print(Fore.RED + "Error! Only integers are allowed!")