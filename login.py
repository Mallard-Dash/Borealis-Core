#login.py
import main
import mariadb

def new_user(conn):
    cur=conn.cursor()
    while True:
        username=input("Please enter username: ")
        password=input("Now choose a good password with at least 4 characters: ")
        password2=input("Enter the same password again: ")

        if password != password2:
            print("Passwords do not match, please try again!")
            continue
        elif password == password2:
            print("User created!")
            try:
                cur.execute("INSERT INTO users(username, passwd)VALUES(?, ?)", (username, password))
                conn.commit()
            except mariadb.Error as e:
                print(f"Error: {e}")
                continue
            login_menu()

def authenticate(conn):
    cur=conn.cursor()
    while True:
        username=input("Enter your username: ")
        password=input("Enter your password: ")
        try:
            res = cur.execute("SELECT username, passwd FROM users WHERE username = (?)", [username])
            conn.commit()
            if res.fetchone() == True:
                print("The user does not exist, try again!")
                continue
            elif res.fetchone(password) !=password:
                print("Wrong password, try again!")
                continue
            else:
                main.main_menu()
        except mariadb.Error as e:
            print(f"Error: {e}")
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
                authenticate(conn=main.database_connection())
            elif first_choice == 2:
                new_user(conn=main.database_connection())
            elif first_choice == 3:
                print("Good bye! :)")
                time.sleep(1)
                break
            else:
                print("Please enter a valid choice!")
        except ValueError:
            print("Error! Only integers are allowed!")

login_menu()