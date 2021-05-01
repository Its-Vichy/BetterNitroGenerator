import threading, requests, random, string, time
from colorama import Fore, Style, init
init()


def printer(color, status, code, info, action, retry, lock= threading.Lock()):
    lock.acquire()
    print(f'{Style.BRIGHT}{Fore.WHITE}[{color}{status}{Fore.WHITE}] [{code}] [{info}] [{action}] [{retry}]')
    lock.release()

class Worker(threading.Thread):
    def config(self, proxy, retry= 2, time_after_retry= 1):
        self.proxy = dict({'http': f'{proxy}', 'https': f'{proxy}'})
        self.time_after_retry = time_after_retry
        self.retry = retry
    
    def run(self):
        total_retry = 0

        while True:
            if total_retry == self.retry:
                printer(Fore.BLACK, 'MTRY', code, ' MAX  RETRY ', 'KILL  WORKER', total_retry)
                break

            code = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(16)])
            try:
                response = requests.get(f'https://discordapp.com/api/v6/entitlements/gift-codes/{code}', headers= {'content-type': 'application/json'}, proxies= self.proxy, timeout= 3500)
                message  = response.json()['message']
                status   = response.status_code

                if status == 200:
                    printer(Fore.GREEN, 'VALI', code, 'VALIDE  CODE', ' SAVE NITRO ', total_retry)
                    
                    with open('./hit.txt', 'a+') as hit:
                        hit.write(code + '\n')

                if message == 'Unknown Gift Code':
                    printer(Fore.MAGENTA, 'INVA', code, 'INVALID CODE', 'CHECK  OTHER', total_retry)
                
                elif message == 'You are being rate limited.':
                    rate = (int(response.json()['retry_after']) / 1000) + 1
                    printer(Fore.YELLOW, 'RATE', code, 'RATE LIMITED', 'SLEEP WORKER', total_retry)
                    time.sleep(rate)
            
            except requests.exceptions.ProxyError as err:
                printer(Fore.LIGHTRED_EX, 'ERRO', code, ' DEAD PROXY ', 'SLEEP WORKER', total_retry)
                time.sleep(60 * self.time_after_retry)
                total_retry += 1
            except requests.exceptions.SSLError as err:
                printer(Fore.CYAN, 'SSL.', code, ' INVA PROXY ', 'KILL  WORKER', total_retry)
                break
            except requests.exceptions.ConnectTimeout as err:
                printer(Fore.BLACK, 'LAG.', code, ' SLOW PROXY ', 'SLEEP WORKER', total_retry)
                time.sleep(60 * self.time_after_retry)
                total_retry += 1
            except requests.exceptions.InvalidProxyURL as err:
                printer(Fore.LIGHTBLUE_EX, 'URL.', code, ' URL. PROXY ', 'KILL  WORKER', total_retry)
                break
            except Exception as err:
                #print(err)
                printer(Fore.RED, 'IDK.', code, 'FATALE ERROR', 'KILL  WORKER', total_retry)
                break

if __name__ == '__main__':
    Proxies = []

    with open('./proxy.txt', 'r+') as proxy_file:
        for proxy in proxy_file:
            Proxies.append(proxy)
    Proxies = list(set(Proxies))
    
    print(f"""{Fore.CYAN} 
         ____       _   _              _   _ {Fore.WHITE}_{Fore.CYAN} _              ____            
        | __ )  ___| |_| |_ ___ _ __  | \ | {Fore.WHITE}(_){Fore.CYAN} |_ _ __ ___  / ___| ___ _ __  
        |  {Fore.WHITE}_{Fore.CYAN} \ / {Fore.WHITE}_{Fore.CYAN} \ __| __/ {Fore.WHITE}_{Fore.CYAN} \ '__| |  \| | | __| '__/ {Fore.WHITE}_{Fore.CYAN} \| |  _ / {Fore.WHITE}_{Fore.CYAN} \ '_ \ 
        | {Fore.WHITE}|_){Fore.CYAN} |  __/ |_| ||  __/ |    | |\  | | |_| | | {Fore.WHITE}(_){Fore.CYAN} | |_| |  __/ | | |
        |____/ \___|\__|\__\___|_|    |_| \_|_|\__|_|  \___/ \____|\___|_| |_|
        https://github.com/{Fore.WHITE}Its-Vichy
        """)

    retry_number = int(input(f'> Max retry/worker: '))
    timer = int(input(f'> Error sleep delay (in minute) (NOT limit sleep): '))

    print()
    for proxy in Proxies:
        Task = Worker()
        Task.config(proxy, retry_number, timer)
        Task.start()