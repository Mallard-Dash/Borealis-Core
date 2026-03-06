#Borealis-Core

import time
from colorama import init, Style,Fore
import mariadb
import sys
from dotenv import load_dotenv
import bedrock_agent
import os
import login
import pyfiglet
import diary
from lolpython import lol_py 
import aws_secretsmanager
import knowledge
load_dotenv()
init(autoreset=True)
secret=aws_secretsmanager.get_secret()

#The following 5 functions are currently not in use
def weight_query():
    database_connection()
    cur=conn.cursor
    user_name = input("Enter your username: ")
    cur.execute("SELECT user_weight FROM daily_data ")

def waist_query():
    database_connection()
    cur=conn.cursor
    user_name = input("Enter your username: ")

def blood_pressure_query():
    database_connection()
    cur=conn.cursor
    user_name = input("Enter your username: ")

def mental_query():
    database_connection()
    cur=conn.cursor
    user_name = input("Enter your username: ")

def stress_query():
    database_connection()
    cur=conn.cursor
    user_name = input("Enter your username: ")

def database_connection():
        conn = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "3306")),
            database="healthlogger"
        )
        return conn

def enter_values(conn, user_id):
    user_id=user_id[0]
    cur=conn.cursor()
    try:
        user_weight=float(input("Please enter todays weight in kgs: "))
        waist=float(input("Please enter the waist in cm: "))
        blood_pressure=input("Please enter your bloodpressure and pulse (OVP/UP-PP): ")
        mental_state=int(input("Enter a number from 1-10 that best describes todays mood (1=shit, 10=hit): "))
        stress=int(input("Please enter a number from 1-10 how stressed you feel today (1=calm, 10=burnout): "))
        if mental_state > 10 or mental_state < 0:
            print("You can only enter values between 1-10")
            return
        if stress > 10 or stress < 0:
            print("You can only enter values between 1-10")
            return
        
        summary=(f"Your summary is: Weight{user_weight}kg\n Waist:{waist}cm\n Blood_pressure:{blood_pressure}| \n Mental_state:{mental_state}/10 \n Stress:{stress}/10")
        #print(summary)
        save_values=input(f"{summary} \n| Save values (y/n)?")
        if save_values.lower() == "y":
            cur.execute("INSERT INTO daily_data(user_id, user_weight, waist, blood_pressure, mental_state, stress)VALUES(?, ?, ?, ?, ?, ?)", (user_id, user_weight, waist, blood_pressure, mental_state, stress))
            conn.commit() 
            print(Fore.GREEN + "Values saved!")
        elif save_values.lower() == "n":
            print(Fore.YELLOW + "Discarding values...")
            return
        else:
            print(Fore.YELLOW + "Discarding values...")
    except ValueError:
        print(Fore.RED + "Error! Please enter only numbers for weight/waist/mental_state/stress ")

def show_values():
    pass


def graph_menu():
    while True:
        try:
            print(f"***Graph menu***\n",
                "1. Weight\n",
                "2. Waist\n",
                "3. Blood-pressure\n",
                "4. Mental-state\n",
                "5. Stress\n",
                "6. Go back\n")
            graph_menu_choice=int(input("Please make a choice: "))
            if graph_menu_choice == 1:
                weight_query()
            elif graph_menu_choice == 2:
                waist_query()
            elif graph_menu_choice == 3:
                blood_pressure_query()
            elif graph_menu_choice == 4:
                mental_query()
            elif graph_menu_choice == 5:
                stress_query()
            elif graph_menu_choice == 6:
                print("Going back...")
                time.sleep(1)
                break
            else:
                print(Fore.RED + "Wrong input, try again.")
        except ValueError:
            print(Fore.RED + "Only integers are allowed.")

            

def main_menu(session, conn, secret):
        print("Connecting to database...")
        time.sleep(0.5)
        print(Fore.GREEN + "Connection established!")
        print("Waking up the ai-agent...")
        time.sleep(1)
        print(Fore.GREEN + "Ai-agent up and running!")
        T = ("Borealis-Core")
        ASCII_art_1 = pyfiglet.figlet_format(T,font='slant')
        print (lol_py(ASCII_art_1))
        while True:
            try:
                print(f"***Main Menu***\n",
                    "1. Enter todays values\n",
                    "2. Access diary\n",
                    "3. Personal-wiki\n",
                    "4. Look at your data\n",
                    "5. AI-chat\n",
                    "6. Log out\n")
                menu_choice=int(input("Welcome to Healthlogger version 2.0! Please make a menu choice: "))
                if menu_choice == 1:
                    enter_values(conn, user_id=session)
                elif menu_choice == 2:
                    diary.sub_menu_diary(session, conn)
                elif menu_choice == 3:
                    knowledge.knowledge_menu(session, conn)
                elif menu_choice == 4:
                    print("This feature is not ready yet!")
                elif menu_choice == 5:
                    bedrock_agent.bedrock_main_menu(secret, session, conn)
                elif menu_choice == 6:
                    print("Exiting...")
                    time.sleep(1)
                    break
                else:
                    print(Fore.RED + "Wrong input, try again.")
            except ValueError:
                print(Fore.RED + "Only integers are allowed")
conn=database_connection()
while True:
    session = login.login_menu(conn)
    if session is None:
        conn.close()
        break
    main_menu(session, conn, secret)
        

