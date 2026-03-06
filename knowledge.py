#Knowledge database
import time
import colorama
import mariadb

def knowledge_menu():
    while True:
        try:
            print("***Knowledge menu***\n",
                "1. Enter new knowledge\n",
                "2. Show knowledge\n",
                "3. Go back\n")
            knowledge_choice = int(input("Pleas enter a choice from 1-3: "))
            if knowledge_choice == 1:
                pass
            elif knowledge_choice == 2:
                pass
            elif knowledge_choice == 3:
                print(Returning...)
                time.sleep(1)
                return
            else:
                print("Please enter a value from 1-3: ")
        except ValueError:
            print("Only integers are allowed!")
        
def categories():
    while True:
        try:
            print("***Categories***\n",
                "1. Identity\n",
                "2. Values\n",
                "3. Goals\n",
                "4. Health\n",
                "5. Mental-Health\n",
                "6. Habits\n",
                "7. Skills\n",
                "8. Career\n",
                "9. Finance\n",
                "10. Technology\n",
                "11. Programming\n",
                "12. Security\n",
                "13. Nature\n",
                "14. Fitness\n",
                "15. Food & Nutrition\n",
                "16. Philosofy\n",
                "17. Psychology\n",
                "18. Relationships\n",
                "19. Communication\n",
                "20. Creativity\n",
                "21. Projects\n",
                "22. Ideas\n",
                "23. Observations\n",
                "24. Lessons Learned\n",
                "25. Random Facts\n",
                "26. EXIT\n")
            cat_choice = int(input("Please choose what category to store this knowledge in: "))
            category_names=["identity", "values", "goals", "health", "mental-health", "habits", "skills",
                    "career", "finance", "technology", "programming", "security", "nature", "fitness", "food-nutrition",
                    "philosofy", "psychology", "relationships", "communication", "creativity", "projects",
                    "ideas", "observations", "lessons-learned", "random-facts", "exit"]
            elif cat_choice == 26:
                print("Returning...")
                time.sleep(1)
                return
        
        except ValueError:
            print("Only integers are allowed")

def save knowledge_entry(cat_choice, conn):
    knowledge = input("Write your knowledge: ")
    categories()
    category = input("What category would you like to put this knowledge in?")
    cur = conn.cursor()
    cur.execute("INSERT INTO knowledge_db (category_id, knowledge_content) WHERE user_id =(?) VALUES(?,?)", (user_id,))