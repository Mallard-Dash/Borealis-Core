#Knowledge database
import time
from colorama import Fore, init
import mariadb
init(autoreset=True)

def knowledge_menu(user_id, conn):
    while True:
        try:
            print("***Knowledge menu***\n",
                "1. Enter new knowledge\n",
                "2. Show knowledge\n",
                "3. Go back\n")
            knowledge_choice = int(input("Pleas enter a choice from 1-3: "))
            if knowledge_choice == 1:
                save_knowledge_entry(user_id, conn)
            elif knowledge_choice == 2:
                show_knowledge(user_id, conn)
            elif knowledge_choice == 3:
                print("Returning...")
                time.sleep(1)
                return
            else:
                print("Please enter a value from 1-3: ")
        except KeyboardInterrupt:
            print("Keyboard Interruption")
        except ValueError:
            print(Fore.RED + "Only integers are allowed!")
        
def categories_menu():
    print("***Categories***")
    category_names = [
        "Identity", "Values", "Goals", "Health", "Mental-Health", "Habits", "Skills",
        "Career", "Finance", "Technology", "Programming", "Security", "Nature", "Fitness", 
        "Food & Nutrition", "Philosofy", "Psychology", "Relationships", "Communication", 
        "Creativity", "Projects", "Ideas", "Observations", "Lessons Learned", "Random Facts"
    ]
    
    for i, name in enumerate(category_names, 1):
        print(f"{i}. {name}")
    print("26. EXIT")
    
    while True:
        try:
            cat_choice = int(input("Please choose what category to store this knowledge in: "))
            if cat_choice == 26:
                return None
            if 1 <= cat_choice <= 25:
                return cat_choice
            else:
                print(Fore.YELLOW + "Please choose a number between 1-26.")
        except KeyboardInterrupt:
            print("Keyboard Interruption")
        except ValueError:
            print(Fore.RED + "Only integers are allowed")

def save_knowledge_entry(user_id, conn):
    cur = conn.cursor()
    # Ensure user_id is an integer (handling tuple if necessary)
    if isinstance(user_id, tuple):
        user_id = user_id[0]
        
    category_id = categories_menu()
    if category_id is None:
        return

    knowledge_content = input("Write your knowledge: ")

    try:
        cur.execute(
            "INSERT INTO knowledge_db (user_id, category_id, knowledge_content) VALUES (?, ?, ?)", 
            (user_id, category_id, knowledge_content)
        )
        conn.commit()
        print(Fore.GREEN + "Knowledge saved to your personal wiki!")
    except KeyboardInterrupt:
        print("Keyboard Interruption")
    except mariadb.Error as e:
        print(Fore.RED + f"Database error: {e}")

def show_knowledge(user_id, conn):
    if isinstance(user_id, tuple):
        user_id = user_id[0]
        
    cur = conn.cursor()
    query = """
        SELECT c.category_name, k.knowledge_content, k.entry_date 
        FROM knowledge_db k
        JOIN knowledge_categories c ON k.category_id = c.category_id
        WHERE k.user_id = ?
        ORDER BY k.entry_date DESC
    """
    cur.execute(query, (user_id,))
    rows = cur.fetchall()
    
    if rows:
        print(Fore.CYAN + "\n--- Your Personal Wikipedia ---")
        for category, content, date in rows:
            print(f"[{date}] {category.upper()}: {content}")
        print("-------------------------------\n")
    else:
        print(Fore.YELLOW + "No knowledge entries found.")