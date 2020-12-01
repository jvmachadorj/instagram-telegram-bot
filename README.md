# Instagram-Telegram-Bot
## What it does
This Telegram bot takes a random picture in pixabay, put a customized subscription and asks you if it can post in your instagram account

In the .env file you need to put your initial settings

```
TOKEN = 'telegramToken'
PIXA_BAY_KEY = 'Pixa bay token'
USERNAME = 'username'
PASSWORD = 'password'
```

### Where to find credentials

The `TOKEN` is the Telegram TOKEN, to create one open Telegram app, search for @BotFather and start the chat. Send /newbot command and follow the instructions.

The `PIXA_BAY_KEY` in the key from <https://pixabay.com/> and to get the jey, head to <https://pixabay.com/api/docs/>. Search for key and login to generate yours.

USERNAME and PASSWORD is from your Instagram account.

You also need a `RiteKit Client ID`, found in here https://ritekit.com/developer/dashboard/

## Setting up your virtual enviroment

I'm supposing you have already installed python in your machine. If not, just follow this <https://realpython.com/installing-python/>

Install pip `sudo apt-get install python3-pip`

After that open your terminal and type `sudo pip3 install virtualenv`

Navigate to the projects directory and excecute `virtualenv -p python3 venv`

To activate `source venv/bin/activate`

## Install Requirements.txt

After installing the virtual env and to activate it, run this code to install all necessary requirements for the project
`pip install -r requirements.txt`

After that you are all Set Up

Just run the command `python main.py`
