Welcome to Borealis-Core!

I thought it was about time to get a hold of this old duster and make som upgrades and implement an ai-feature.
This version is not built on top of the previous version, it is a complete remake from scratch.

18 february 2026: I've created the necessary files and some menu functions. I haven't decided what agent-model I will use just yet, but as RDBMS I will go for
Mariadb which also gives me an excuse to use Docker also.

20 february 2026: I have sucessfully implemented the ai-LLM from aws, the DB is up and running in a docker-container and most of the functionality in the menus
is on the way. I have also installed a nice logo that will show at start. 

21 february 2026: I sat for like 2 hours with a annoying problem with the imports file to file. Oh yeah and I also added a user-session with login, user creation and passwords. I will implement a hashing for the passwords also in the future.

22 february 2026: The application is mostly functional now :) I had som real struggle with the SQL-syntax to get Python and Mariadb to talk to each other. The ai-function is only an ai-chat now, but in the next version I will have fixed this so that the LLM can have access to the users health-data in the db. Also
I added a hash-function for the password-handling.