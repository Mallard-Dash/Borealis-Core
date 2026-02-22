#-----------------------------------------------------------------------------------------------------------
#Borealis-Core
#-----------------------------------------------------------------------------------------------------------

This is an application created firsthand for my own sake because I really like to keep track of important data. And what could be more important than
your own health? We all love to code and develop projects, but we also need to make our bodies last many many years. That's why I made this application.
The user can log weight, waist-measure, blood-pressure, stress, and overall mood. The last two values is entered with a number on a scale from 1-10,
you get the picture.

##So where does AI come into the picture? 
Any way you want to! In the first version as i'm writing this, the LLM is only a chat in a while-loop that sends/recieves requests from AWS Bedrock. But in future
versions I would like to give the LLM access to user-data so it can give comments and such on the users health. Or just chat with it like a friend.

##DISCLAIMER!
Firstly, I am no doctor nor do I have medical education, and the same thing goes for the LLM-ai. If you feel ill or that something ain't right,
then don't hesitate to contact a real medical professional. As I said before, this application is only for my own educational purpose.

##Secondly

The ai-LLM from AWS-bedrock is using keys from my own AWS and I tend to keep it that way. That means the application will surely be broken
if you try to run it as it is. I will write instructions you can follow if you have your own AWS and want to call on an ai-LLM. If you are skilled
you could try to rebuild the 'bedrock-agent.py' to suit API-calls from another LLM-provider, just write what you've changed if you want to redistribute. :)

##Where did the idea come from?
Because I did a simmilar program like this at the very beginning of my code journey. This program is written with fresh code from scratch, the only thing
the programs share are the ideas and concepts. 
This is the git-repo for my old program called healthlogger: [text](https://github.com/Mallard-Dash/Healthlogger_git)


###Techstack Borealis-Core

Python
Docker
Mariadb
AWS-Bedrock
SQL 

