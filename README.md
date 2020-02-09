# cs50finalproject
final project in cs50

Introduction:

This project is a web-based application turn-based game that takes inspiration from Pokemon's battle interface.

It is very simple and consists of:
- One on one turn-based battle system with each monster.
- A dice roll function which determines the amount of damage you deal or the effectiveness of your skills.
- Two classes: healer and a warrior, healer has a skill named heal and warrior has a skill named slash:
  - Heal recovers your character's HP based on the dice rolled multipled by 2.
  - Slash deals damage to the monster you are against based on the dice rolled multiplied by 2.
- 3 levels, each level consist of 3 monsters and each monster has the same amount of HP:
  - Monsters in higher levels have a greater amount of HP, but the amount of damage they potentially do is capped by the highest number outputted
  by the dice function which is 6.
- Replayability: Everytime you beat the game, it asks you if you'd like to restart, if you choose to restart, then it'll add a value of 5 to your character's
HP and MP and to the monster's HP as well.

Pages on the web-application:
- Create character: which allows you to create your characters
- Map: which showcases the monsters on that current level
- Fight: which allows you to battle a monster 1 on 1 (you cannot choose the monster you want to fight, has to be fought sequentially according to monsters'
order in they appear and also level)
- Rest: which allows your character to regain his full HP and MP
- Home: displays your characters' stats and their current location

Languages
- JavaScript, Python, HTML/CSS, SQL

Frameworks used:
- Flask

Code used from CS50:
- Layout.html was used from CS50 library, except for the JavaScript code which was added by me to verify whether the user 
has created a character.
- Functions provided in the helpers.py such as apology and login_required

Pictures:
- Arrow.png and giphy.gif used in the project belong to their respective owners and I do not claim any right over them.

Future works:
- Game will be made more fun, and the battle system will be changed so it's not just based on luck.