# Borealis-Core

Borealis-Core is an application I created for myself because I like keeping track of important data—and what could be more important than your health?

The user can log:

- Weight
- Waist measurement
- Blood pressure
- Stress (1–10)
- Overall mood (1–10)

## Where does AI come into the picture?

Anywhere you want it to.

In the first version (as I’m writing this), the LLM is only a chat running in a while-loop that sends/receives requests from AWS Bedrock. In future versions, I’d like to give the LLM access to user data so it can comment on health trends, provide insights, and generally chat like a friend.

## Disclaimer

### Medical disclaimer

I am not a doctor and I have no medical education—and the same goes for the LLM. If you feel ill or something isn’t right, contact a real medical professional.

This application is for my own educational purposes.

### AWS / LLM keys disclaimer

The AWS Bedrock LLM uses keys from my personal AWS account, and I intend to keep it that way. This means the application will likely be broken if you try to run it as-is.

I will write instructions you can follow if you have your own AWS account and want to call an LLM. If you are skilled, you could also rebuild `bedrock-agent.py` to use API calls from another LLM provider—just document what you changed if you redistribute.

## Where did the idea come from?

I built a similar program at the very beginning of my coding journey. This program is written fresh from scratch; the only thing they share are the ideas and concepts.

Old program repo: [healthlogger](https://github.com/Mallard-Dash/Healthlogger_git)

## Tech stack

- Python
- Docker
- MariaDB
- AWS Bedrock
- SQL
