## Telegram-bot

Telegram bot to monitor your homework's status. Made during Yandex.Practicum.
Sends messages if there's an update to your homework.


### Stack:

![Python](https://img.shields.io/badge/Python_3.9.8-%23254F72?style=for-the-badge&logo=python&logoColor=yellow&labelColor=254f72)<br>
![dotenv](https://img.shields.io/badge/python--dotenv_0.19.0-%23254F72?style=for-the-badge&logo=python&logoColor=yellow&labelColor=254f72)<br>
![TelegramBot](https://img.shields.io/badge/python--telegram--bot_13.7-28A4E4?style=for-the-badge&logo=telegram&logoColor=white&labelColor=28A4E4)


### Running this bot:

- Clone project:

```
git@github.com:nikpetrischev/homework_bot.git
```

- Switch to project's folder:

```
cd homework_bot
```

- Create virtual environment:

```
python -m venv env
```

- Activate it:

```
source env/bin/activate
```

- Install requirements:

```
pip install -r requirements.txt
```

- Pass into .env file all of the required tokens:
- - Yandex.Practicum profile token:<br>
<a href="https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a" target="_blank">Get token</a>
- - Bot token from @BotFather:<br>
<a href="https://t.me/BotFather" target="_blank">BotFather</a>
- - Telegram UserID (can get from @Userinfobot):<br>
<a href="https://t.me/userinfobot" target="_blank">UserInfo</a>

- Run bot:

```
python homework.py
```

- Enjoy!


##
Bot made by Nikolai Petrishchev