#This file is responsible for the calling of the AWS-bedrock agent
import boto3
import json
from botocore.exceptions import ClientError
#from dotenv import load_dotenv
import os
from colorama import Fore, Style, init
from aws_secretsmanager import get_secret
init(autoreset=True)
#load_dotenv()


def call_agent(secret):
    chat_history = []

    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    # Set the model ID, e.g., Claude 3 Haiku.
    model_id = "us.anthropic.claude-sonnet-4-6"

    # Define the prompt for the model. This prompt is just a test to see if it works (it does)
    system_prompt = "You are my assistant You only speak swedish and are old-fashioned."
    while True:
        user_input=input("You:")
        chat_history.append({"role": "user", "content": [{"type": "text", "text": user_input}]})
        if user_input.lower() == "exit":
            break

        # Format the request payload using the model's native structure.
        native_request = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "temperature": 0.5,
                "system": system_prompt,
                "messages": chat_history
            }

        try:
            response = client.invoke_model(modelId=model_id, body=json.dumps(native_request))
            model_response = json.loads(response["body"].read())
            ai_text = model_response["content"][0]["text"]
            print(Fore.CYAN + f"AI: {ai_text}.")
            chat_history.append({"role": "assistant", "content": [{"type": "text", "text": ai_text}]})

        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
            exit(1)

secret=get_secret()
#This is here for testing and not in use right now
#call_agent(secret) 

