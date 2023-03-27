### Telegram-bot

```
Telegram bot for tracking the status of homework checks on Yandex.Practicum.
Sends messages when the status is changed - taken for review, has remarks, passed.
```

### Technologies:
- Python 3.9
- python-dotenv 0.19.0
- python-telegram-bot 13.7

### How to run the project:

Clone the repository and navigate to it in the command line:

```
git clone git@github.com:ya_yura/homework_bot.git
```

```
cd homework_bot
```

Create and activate a virtual environment:

```
python -m venv env
```

```
source env/Scripts/activate
```

Install dependencies from the requirements.txt file:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Write the necessary keys to environment variables (in the .env file):

- token for your profile on Yandex.Practicum
- token for the Telegram bot
- your ID in Telegram

Run the project:

```
python homework.py
```
