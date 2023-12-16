import threading, requests, time, os, settings

class Scanner(threading.Thread):
    def __init__(self, wallet_address:str,callback_function,proxy:str="",interval:int=settings.get("scanner_interval")):
        self.session = requests.Session()
        if proxy: self.set_proxy(proxy)
        self.wallet_address = wallet_address
        self.interval = interval
        self.callback_function = callback_function
        self.txh_path = os.path.join(os.getcwd(),f"last_txs\\{wallet_address}")
        self.last_tx_id = self.init_txh()
        super().__init__()

    def set_proxy(self,proxy:str):
        proxy_data = proxy.split(':')
        ip = proxy_data[0]
        port = proxy_data[1]
        user = proxy_data[2]
        passw = proxy_data[3]
        proxy = f"http://{user}:{passw}@{ip}:{port}/"
        self.session.proxies = {"http":proxy,"https":proxy}

    def init_txh(self):
        if not os.path.exists(self.txh_path):
            self.write_txh(0)
        with open(self.txh_path,"r") as f:
            return int(f.read())

    def write_txh(self,data):
        with open(self.txh_path,"w") as f:
            f.write(str(data))

    def run(self):
        print(f"{self.wallet_address}: tracker started")
        while True:
            transfers = self.get_spl_transfers()
            if not transfers:
                time.sleep(self.interval)
                continue
            for tx in sorted(transfers.items(),reverse=True):
                tx_id = tx[0]
                if self.last_tx_id==tx_id: break
                print(f"{self.wallet_address}: new transfers pushed")
                self.callback_function(tx)

            self.last_tx_id = max(transfers.keys())
            self.write_txh(self.last_tx_id)
            time.sleep(self.interval)

    def get_spl_transfers(self):
        transfers = {}
        response_exists = False
        while not response_exists:
            try:
                response = self.session.get(f"https://api.solscan.io/v2/account/token/txs?address={self.wallet_address}&offset=0&limit=10&cluster=",
                headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"})
                response_exists = True
            except Exception as e:
                print(f"{self.wallet_address}: {e}")
                time.sleep(self.interval)

        if response.status_code!=200:
            print(f"{self.wallet_address}: response status code={response.status_code}")
            return transfers
        response = response.json()
        #print(response)
        for tx in response["data"]["tx"]["transactions"]:
            #if "symbol" in tx["change"]:
            token = tx["change"]["tokenAddress"]
            amount = int(tx["change"]["changeAmount"])*10**-9
            pre_balance = int(tx["change"]["preBalance"])*10**-9
            post_balance = int(tx["change"]["postBalance"])*10**-9
            tx_id = tx["slot"]
            sig = tx["txHash"]
            transfers[tx_id] = {
                "address":self.wallet_address,
                "token":token,
                "amount":amount,
                "pre_balance":pre_balance,
                "post_balance":post_balance,
                "sig":sig
            }
        return transfers

class ScannerHandler(threading.Thread):
    def __init__(self,interval=settings.get("scanner_handler_interval")):
        self.proxies = []
        self.scanners = []
        self.interval = interval
        self.queue = []
        self.set_proxies_list()
        super().__init__()
    
    def run(self):
        while True:
            if self.queue:
                self.queue[0].start()
                if self.proxies: self.queue[0].set_proxy(self.proxies[0])
                self.scanners.append(self.queue[0])
                self.queue.pop(0)
                if self.proxies: self.proxies.pop(0)
            time.sleep(self.interval)

    def add(self,scanner:Scanner):
        self.queue.append(scanner)

    def set_proxies_list(self,filename="proxy.txt"):
        with open(filename,"r") as f:
            self.proxies = f.read().split("\n")
            for proxy in self.proxies:
                if proxy == '': self.proxies.remove(proxy)
        print(self.proxies)

if __name__ == "__main__":
    sc = Scanner("B46Le8hykyy9SgFaM6DrBDw5tW7dezgGv3vqKQdPMTHX",print)
    sc.start()
    #print(sc.get_spl_transfers().sort())