import settings
import os

def init():
    print("dir",os.listdir())
    if "settings.json" not in os.listdir(): settings.init()
    if "proxy.txt" not in os.listdir(): open("proxy.txt","w").close()
    if "last_txs" not in os.listdir(): os.mkdir("last_txs")

init()

from scanner import Scanner
from bot import bot, callback_function, scanner_handler

if __name__ == "__main__":
    for wallet in settings.get_wallets():
        scanner_handler.add(Scanner(wallet,callback_function))
    bot.polling(none_stop=True, interval=0)