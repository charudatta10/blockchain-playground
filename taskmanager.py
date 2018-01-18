
import atexit
import os
import subprocess
import requests
import json
import time
import random
from threading import Thread
from multiprocessing import Lock


class BlockchainTest(object):

    def __init__(self, num_nodes = 5):
        self.running = False
        self.mining = False

        self.mutex = Lock()
        self.global_increment = 1

        self.processes = []
        self.miners = []
        self.ts_worker = None
        
        self.port_base = 5000
        self.start_nodes(num_nodes)
        self.start_worker()


    def start_nodes(self, num_nodes):
        self.running = True
        silent_mode = open(os.devnull, 'wb')
        self.processes = [
           subprocess.Popen("python app.py %d"%(self.port_base+i), stdout=silent_mode, stderr=silent_mode)
           for i in range(num_nodes)
        ]
        silent_mode.close()
        
        for i in range(num_nodes):
            port = self.port_base + i
            url = "http://localhost:%d/nodes/register"%port
            data = []
            for j in range(self.port_base, self.port_base+i):
                if j == port: continue
                data.append("http://localhost:%d/"%j)
                
            response = requests.post(
                url,
                data = json.dumps({'nodes':data}),
                headers = {'content-type': 'application/json'}
            )
        

    def stop_nodes(self):
        self.mining = False
        self.running = False

        # kill all subprocesses
        for i, process in enumerate(self.processes):
            if process.poll() is None: # process is not terminated
                process.kill()


    def start_worker(self):
        self.ts_worker = Thread(
            target = self.run_transaction,
            name = None,
            args = ())
        self.ts_worker.start()

    
    def start_miners(self, sec_interval=6):
        self.mining = True
        n = len(self.processes)
        self.miners = [
            Thread(None, target=self.mine, name="Miner-%d"%i, args=(self.port_base+i, sec_interval + 3 * i))
            for i in range(n)
        ]

        for t in self.miners:
            t.start()


    def stop_miners(self):
        self.mining = False


    def mine(self, port, interval):
        while True:
            if not self.running or not self.mining:
                break
            url = "http://localhost:%d/nodes/resolve"%port
            response = requests.get(url)

            url = "http://localhost:%d/mine"%port
            response = requests.get(url)
            time.sleep(interval)


    def run_transaction(self):
        time.sleep(3)
        while True:
            if not self.running:
                break
            with self.mutex:
                self.new_transaction()


    def new_transaction(self, node_index = None):
        
        for node_index in range(0, len(self.processes)):
            if random.randint(0, 10) < 3:
                continue

            port = self.port_base + node_index
            try:
                url = "http://localhost:%d/transactions/new"%port
                headers = {'content-type':'application/json'}
                requests.post(url, data=json.dumps({
                    'sender': 'test-sender',
                    'recipient': 'test-recipient',
                    'amount': self.global_increment
                }), headers = headers)

            except Exception as e:
                print e.message
        
        self.global_increment += 1


    def snapshot(self):
        if not self.running:
            print "simulation not running"
            return

        n = len(self.processes)
        max_ts_amount = 0
        num_ts = 0
        for i in range(n):
            port = self.port_base + i
            url = "http://localhost:%d/chain"%port
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    res = response.json()
                    obj = {
                            'node': port,
                            'length': res['length'],
                            'transactions': [len(block['transactions']) for block in res['chain']]
                        }
                    for block in res['chain']:
                        for ts in block['transactions']:
                            if ts['amount'] > max_ts_amount:
                                max_ts_amount = ts['amount']
                    num_ts = max([num_ts, sum(obj['transactions'])])
                    print obj

            except Exception as e:
                print e.message
        
        print "transaction loss:", 1.0 - (1.0 * (num_ts+1) / (max_ts_amount+1))



def mainloop():

    manager = BlockchainTest(num_nodes=5)
    atexit.register(manager.stop_nodes)

    while True:
        cmd = raw_input('>')
        cmd = cmd.lower()
        if cmd == "snapshot" or cmd == "ss":
            manager.snapshot()
        elif cmd == "start":
            manager.start_miners()
        elif cmd == "stop":
            manager.stop_miners()
        elif cmd == "exit" or cmd == "quit" or cmd == "q":
            manager.stop_nodes()
            break
        else:
            print "bad command"


if __name__ == "__main__":
    mainloop()