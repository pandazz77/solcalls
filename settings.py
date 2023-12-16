import json

_CONTENT = """
{   
    "token": "bot_token",
    "scanner_interval":10,"scanner_handler_interval":10, 
    "wallets": [], 
    "users": []
}
"""

def init():
    with open("settings.json", "w") as f:
        f.write(_CONTENT)

def read():
    with open("settings.json","r") as f:
        return json.loads(f.read())

def write(data:dict):
    with open("settings.json","w") as f:
        f.write(json.dumps(data))

def get(key:str):
    return read()[key]

def add_wallet(wallet:str):
    data = read()
    if wallet in data["wallets"]: return
    data["wallets"].append(wallet)
    write(data)

def rem_wallet(wallet:str):
    data = read()
    if wallet in data["wallets"]: return
    data["wallets"].remove(wallet)
    write(data)

def get_wallets():
    return read()["wallets"]

def get_users():
    return read()["users"]

def add_user(user_id:int):
    data = read()
    if user_id in data["users"]: return
    data["users"].append(user_id)
    write(data)

def rem_user(user_id:int):
    data = read()
    data["users"].remove(user_id)
    write(data)