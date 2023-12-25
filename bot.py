import telebot, settings
from scanner import Scanner, ScannerHandler
from time import sleep

bot = telebot.TeleBot(settings.read()["token"])
scanner_handler = ScannerHandler()
scanner_handler.start()
markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = telebot.types.KeyboardButton("Add wallet")
btn2 = telebot.types.KeyboardButton('Remove wallet')
btn3 = telebot.types.KeyboardButton("Get wallets")
markup.add(btn1, btn2, btn3)
stages = {}

def callback_function(tx):
    tx_id = tx[0]
    tx_data = tx[1]
    users = settings.get_users()
    amount = tx_data["amount"]
    if amount>0: change = "BUY"
    else: change = "SELL"
    text = f'https://solscan.io/tx/{tx_data["sig"]}\n\nWALLET: {tx_data["address"]}\n{change} {tx_data["amount"]}\nTOKEN:{tx_data["token"]}\nPreBalance: {tx_data["pre_balance"]}\nPostBalance: {tx_data["post_balance"]}'
    while True:
        try:
            for user_id in users:
                bot.send_message(user_id,text)
            break
        except Exception as e:
            print(e)
            print("sleeping for 10s")
            sleep(10)

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id not in settings.get_users(): return
    #settings.add_user(message.from_user.id)
    bot.send_message(message.from_user.id, "Hello, im SolTraderTracker", reply_markup=markup)
    if message.from_user.id in stages: stages.pop(message.from_user.id)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.from_user.id in stages:
        if stages[message.from_user.id] == "add_wallet":
            new_wallet = message.text
            scanner_handler.add(Scanner(new_wallet,callback_function))
            settings.add_wallet(new_wallet)
            users = settings.get_users()
            for user in users:
                bot.send_message(user,f"{message.from_user.username} added {new_wallet} to tracked wallets")

            stages.pop(message.from_user.id)
            

        elif stages[message.from_user.id] == "remove_wallet":
            rem_wallet = message.text
            settings.rem_wallet(rem_wallet)
            bot.send_message(message.from_user.id,f"{rem_wallet} removed")
            stages.pop(message.from_user.id)

    if message.text == 'Add wallet':
        stages[message.from_user.id] = "add_wallet"
        bot.send_message(message.from_user.id,"Input wallet to add:")
    elif message.text == "Remove wallet":
        stages[message.from_user.id] = "remove_wallet"
        bot.send_message(message.from_user.id,"Input wallet to remove:")
    elif message.text == "Get wallets":
        text = "Tracked wallets:\n\n"
        for wallet in settings.get_wallets(): text+=wallet+"\n"
        bot.send_message(message.from_user.id,text,reply_markup=markup)
