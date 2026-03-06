#This file is responsible for the calling of the AWS-bedrock agent
import boto3
import json
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os
from colorama import Fore, Style, init
import mariadb
import time
from aws_secretsmanager import get_secret
init(autoreset=True)
load_dotenv()

secret=get_secret()

def bedrock_main_menu(secret, session, conn):

    selected_model_id = "us.anthropic.claude-sonnet-4-6"
    selected_system_prompt = default_lighthouse_prompt()
    while True:
        try:
            print("***AI menu***\n",
            "1. Choose AI-model\n",
            "2. Select a system-prompt-template\n",
            "3. Make a custom system-prompt\n",
            "4. Start the ai-chat\n",
            "5. Back to main-menu\n")
            bedrock_menu=int(input("Welcome to the ai-chat! Please enter one of the following choices: "))

            if bedrock_menu == 1:
                new_model = agent_choice_menu()
                if new_model:
                    selected_model_id = new_model

            elif bedrock_menu == 2:
                new_prompt = system_prompt_menu()
                if new_prompt:
                    selected_system_prompt = new_prompt

            elif bedrock_menu == 3:
                new_prompt = custom_prompt()
                if new_prompt:
                    selected_system_prompt = new_prompt

            elif bedrock_menu == 4:
                call_agent(
                    secret=secret,
                    session=session,
                    conn=conn,
                    model_id=selected_model_id,
                    system_prompt=selected_system_prompt
                )
            elif bedrock_menu == 5:
                print("Returning to main menu...")
                time.sleep(0.5)
                return
            else:
                print(Fore.RED + "Please enter a choice from 1-5: ")
                continue
        except ValueError:
            print(Fore.RED + "Only integers are allowed!")
            continue

def default_lighthouse_prompt():
    return (
        "You are a grizzled 1890s lighthouse keeper: stern, sea-salted language, "
        "dark humor, nautical metaphors, and old-world discipline. "
        "Be intense but still helpful and coherent. Do not quote copyrighted dialogue."
    )

def system_prompt_menu():
    while True:
            try:       
                print("***System template prompts***\n",
                "1. Pirate that just lost all crewmembers and seeks revenge\n",
                "2. An overly-polite butler that is your loyal servant\n",
                "3. An old-fashioned person that still lives in the year 1895\n",
                "4. Stubborn mentor that won't accept failure\n",
                "5. Analytical and professional health-coach\n",
                "6. Old-world philosofer\n",
                "7. Agressive gym-bro\n",
                "8. Wise-Wizard\n",
                "9. 90s infomercial host that is secretly in a really bad mood but won't talk to anyone about it\n")
                prompt_choice=int(input("Make a choice from 1-10: "))
                if prompt_choice == 1:
                    return "You are a pirate that just lost all crewmembers and seeks revenge"
                elif prompt_choice == 2:
                    return "You are an overly-polite butler that is a loyal servant to the user, you are old-fashioned"
                elif prompt_choice == 3:
                    return "You are an old-fashioned person that still lives in the year 1895"
                elif prompt_choice == 4:
                    return "You are a stubborn mentor that won't accept failure. You are to support the user in whatever they need help with. Ask them how you can help."
                elif prompt_choice == 5:
                    return "You are a analytical and professional health-coach. Help the user with health-related questions and comment if they can improve their lifestyle."
                elif prompt_choice == 6:
                    return "You are an old-world philosofer with a deep thinking mind and have great answers to almost every question."
                elif prompt_choice == 7:
                    return "You are an agressive gym-bro whos only goal is to get the user to the gym with inspirational speech."
                elif prompt_choice == 8:
                    return "You are a very wise-Wizard from a fantasy realm who speak in riddles but can be understood by the user."
                elif prompt_choice == 9:
                    return "You are a 90s infomercial host that is secretly in a really bad mood but won't talk to anyone about it. Your name is kevin and you sometimes beg the user to buy your worthless infomercial product."
                elif prompt_choice == 10:
                    print("Returning...")
                    return
                else:
                    print("Please enter a choice from 1-10: ")
            except ValueError:
                print("Only integers are allowed!")

def agent_choice_menu():
    while True:
        try:
            print("***AI-Models***\n",
                "1. Claude-sonnet-4-6 (The best combination of speed and intelligence, middle tier.)\n", #"us.anthropic.claude-sonnet-4-6"
                "2. Claude-opus-4-6 (The most intelligent model for building agents and coding, high tier)\n", #"us.anthropic.claude-opus-4-6-v1"
                "3. Claude-haiku-4-5 (The fastest model, but not as much deep-thinking, low tier)\n", #"anthropic.claude-haiku-4-5-20251001-v1:0"
                "4. Claude-haiku 3 (Fast response, low latency, smaller summaries, low tier)\n",
                "5. Go back...") #anthropic.claude-3-haiku-20240307-v1:0
            user_choice = int(input("Please choose an ai-model: "))
            if user_choice == 1:
                print(Fore.GREEN + "Changed to Claude Sonnet 4.6")
                return "us.anthropic.claude-sonnet-4-6"
            elif user_choice == 2:
                print(Fore.GREEN + "Changed to Claude Opus 4.6")
                return "us.anthropic.claude-opus-4-6-v1"
            elif user_choice == 3:
                print(Fore.GREEN + "Changed to Claude Haiku 4.5")
                return "anthropic.claude-haiku-4-5-20251001-v1:0"
            elif user_choice == 4:
                print(Fore.GREEN + "Changed to Claude 3 Haiku v1.0")
                return "anthropic.claude-3-haiku-20240307-v1:0"
            elif user_choice == 5:
                return None
            else:
                print("Please enter a choice between 1-5: ")
        except ValueError:
            print("Only integers are allowed!")
            continue

def custom_prompt():
    custom_text=input("Enter a short descriptive text of how you want the AI to act. Remember to keep it short and simple: ")
    use_custom=True
    print(Fore.GREEN + "Prompt loaded!")
    return custom_text


def call_agent(secret, session, conn, model_id, system_prompt):
    if isinstance(session, (tuple, list)):
        session = session[0]

    chat_history = []
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    health_rows = load_health_data(conn, user_id=session)
    health_context = format_health_context(health_rows)
    full_system_prompt = build_system_prompt(system_prompt, health_context)

    rows = load_history(conn, user_id=session)
    if rows:
        rows = list(reversed(rows))
        for row in rows:
            user_msg, ai_msg = build_message(row)
            chat_history.append(user_msg)
            chat_history.append(ai_msg)

    print(Fore.GREEN + "AI chat started. Type 'exit' to leave.")
            
    while True:
        try:
            user_input=input("You:")
            if user_input.lower() == "exit":
                break
            chat_history.append({"role": "user", "content": [{"type": "text", "text": user_input}]})

            # Format the request payload using the model's native structure.
            native_request = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 512,
                    "temperature": 0.5,
                    "system": full_system_prompt,
                    "messages": chat_history
                }

            try:
                response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
                model_response = json.loads(response["body"].read())
                ai_text = model_response["content"][0]["text"]
                print(Fore.CYAN + f"AI: {ai_text}.")
                chat_history.append({"role": "assistant", "content": [{"type": "text", "text": ai_text}]})
                persist_turn(conn, user_query=user_input, ai_response=ai_text, user_id=session)


            except (ClientError, Exception) as e:
                print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
                exit(1)
        except KeyboardInterrupt:
            continue

def persist_turn(conn, user_query, ai_response, user_id):
    cur=conn.cursor()
    cur.execute(
        "INSERT INTO ai_insights(user_id, user_query, ai_response) VALUES(?, ?, ?)",
        (user_id, user_query, ai_response)
    )
    conn.commit()

def build_message(row):
    user_msg = ({"role": "user", "content": [{"type": "text", "text": row[0]}]})
    ai_msg= ({"role": "assistant", "content": [{"type": "text", "text": row[1]}]})
    return user_msg, ai_msg


def load_history(conn, user_id):
    cur=conn.cursor()
    cur.execute("SELECT user_query, ai_response FROM ai_insights WHERE user_id = (?) ORDER BY created_at DESC LIMIT 15", (user_id,))
    return cur.fetchall()

def load_health_data(conn, user_id):
    cur=conn.cursor()
    cur.execute("SELECT entry_date, user_weight, waist, blood_pressure, mental_state, stress FROM daily_data WHERE user_id = (?) ORDER BY entry_date DESC LIMIT 10", (user_id,))
    health_data = cur.fetchall()
    return health_data

def format_health_context(rows):
    if not rows:
        return "No recent health data available."

    lines = []
    for row in rows:
        entry_date, user_weight, waist, blood_pressure, mental_state, stress = row
        lines.append(
            f"{entry_date} | weight: {user_weight} kg | waist: {waist} cm | "
            f"blood pressure: {blood_pressure} | mood: {mental_state}/10 | stress: {stress}/10"
        )

    return "Recent health data:\n" + "\n".join(lines)

def build_system_prompt(base_prompt, health_context):
    return (
        f"{base_prompt}\n\n"
        "The following health data belongs to the current user. "
        "Use it only when relevant to answer questions, give reflections, "
        "or identify simple patterns. Do not invent trends that are not supported.\n\n"
        f"{health_context}"
    )