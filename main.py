#Healthlogger 2.0

import time
import colorama
#import Mariadb

def database_connection():
    pass

def enter_values():
    weight=float(input("Please enter todays weight in kgs: "))
    waist=float(input("Please enter the waist in cm: "))
    blood_preassure=input("Please enter your bloodpreassure and pulse (OVP/UP-PP): ")
    mental_state=int(input("Enter a number from 1-10 that best describes todays mood (1=shit, 10=hit): "))
    stress=int(input("Please enter a number from 1-10 how stressed you feel today (1=calm, 10=burnout): "))
    
    summary=(f"Your summary is: {weight:1f} kg\n {waist:1f} cm\n {blood_preassure} \n 0--{mental_state}--10 \n 1--{stress}--10")
    save_values=input("Save values (y/n) ?")
    if save_values == "y" or "Y":
        pass
    elif save_values == "n" or "N":
        pass

def show_values():
    pass

def sub_menu_diary():
    while True:
        try:
            diary_menu_choice=int(input("Please make a choice: "))
            print(f"***Diary menu***\n",
                "1. Show available diaries\n",
                "2. Write a new entry\n",
                "3. Print an entry\n",
                "4. Go back\n")
            if diary_menu_choice == 1:
                pass
            elif diary_menu_choice == 2:
                pass
            elif diary_menu_choice == 3:
                pass
            elif diary_menu_choice == 4:
                print("Going back...")
                time.sleep(1)
                break
            else:
                print("Wrong input, please try again.")
        except ValueError:
            print("Only integers are allowed, try again.")

def graph_menu():
    while True:
        try:
            graph_menu_choice=int(input("Please make a choice: "))
            print(f"***Graph menu***\n",
                "1. Weight\n",
                "2. Waist\n",
                "3. Blood-preassure\n",
                "4. Mental-state\n",
                "5. Stress\n",
                "6. Go back\n")
            if sub_menu_diary == 1:
                pass
            elif sub_menu_diary == 2:
                pass
            elif sub_menu_diary == 3:
                pass
            elif sub_menu_diary == 4:
                pass
            elif sub_menu_diary == 5:
                pass
            elif sub_menu_diary == 6:
                print("Going back...")
                time.sleep(1)
                break
            else:
                print("Wrong input, try again.")
        except ValueError:
            print("Only integers are allowed.")

def main_menu():
    while True:
        try:
            print(f"***Main Menu***\n",
                  "1. Enter todays values\n",
                  "2. Access diary\n",
                  "3. Look at graphs\n",
                  "4. AI-features\n",
                  "5. Exit\n")
            menu_choice=int(input("Welcome to Healtlogger version 2.0! Please make a menu choice: "))
            if menu_choice == 1:
                pass
            elif menu_choice == 2:
                sub_menu_diary()
            elif menu_choice == 3:
                graph_menu()
            elif menu_choice == 4:
                pass
            elif menu_choice == 5:
                print("Exiting...")
                time.sleep(2)
                break
            else:
                print("Wrong input, try again.")
        except ValueError:
            print("Only integers are allowed")
main_menu()

