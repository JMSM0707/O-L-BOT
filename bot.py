from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout,
    WSMessage
)
from aiohttp_socks import ProxyConnector
from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
import asyncio, random, base64, uuid, json, os, pytz

wib = pytz.timezone('Europe/Moscow')

class OepnLedger:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.openledger.xyz",
            "Referer": "https://testnet.openledger.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.extension_id = "chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc"
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Oepn Ledger - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('manual_proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'manual_proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('manual_proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)
    
    def generate_id(self):
        return str(uuid.uuid4())
        
    def generate_worker_id(self, account: str):
        identity = base64.b64encode(account.encode("utf-8")).decode("utf-8")
        return identity
        
    def hide_account(self, account: str):
        hide_account = account[:6] + '*' * 6 + account[-6:]
        return hide_account
        
    async def renew_token(self, account: str, proxy=None):
        token = await self.generate_token(account, proxy)
        if not token:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Failed to Renew Access Token {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
            return
        
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN + Style.BRIGHT} Access Token Has Been Renewed {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )
        return token
    
    async def generate_token(self, account: str, proxy=None, retries=5):
        url = "https://apitn.openledger.xyz/api/v1/auth/generate_token"
        data = json.dumps({"address":account})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['token']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def user_reward(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/reward"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.renew_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['totalPoint']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def worker_reward(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/worker_reward"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.renew_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data'][0]['heartbeat_count']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None

    async def realtime_reward(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/reward_realtime"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.renew_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data'][0]['total_heartbeats']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
    
    async def checkin_data(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/claim_details"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.renew_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
    
    async def claim_checkin(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/claim_reward"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.renew_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2)
                else:
                    return None
                
    async def user_earning(self, account: str, token: str, proxy=None):
        while True:
            reward = 0
            heartbeat = 0
            heartbeat_today = 0

            user_reward = await self.user_reward(account, token, proxy)
            if user_reward:
                reward = float(user_reward)

            worker_reward = await self.worker_reward(account, token, proxy)
            if worker_reward:
                heartbeat = float(worker_reward)

            realtime_reward = await self.realtime_reward(account, token, proxy)
            if realtime_reward:
                heartbeat_today = float(realtime_reward)

            total_point = reward + heartbeat

            self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Earning {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Total {total_point} PTS{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Today {heartbeat_today} PTS{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
            await asyncio.sleep(600)
                
    async def send_register_msg(self, wss, account: str, id: str, identity: str):
        try:
            register_message = {
                "workerID": identity,
                "msgType": "REGISTER",
                "workerType": "LWEXT",
                "message": {
                    "id": id,
                    "type": "REGISTER",
                    "worker": {
                    "host": self.extension_id,
                    "identity": identity,
                    "ownerAddress": account,
                    "type": "LWEXT"
                    }
                }
            }

            await wss.send_json(register_message)
            return self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Worker ID {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{self.hide_account(identity)}{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}Register Message Sended{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
        except Exception as e:
            return self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Send Register Message Failed {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )

    async def send_heartbeat_msg(self, wss, account: str, identity: str, memory: int, storage: str):
        try:
            heartbeat_message = {
                "message": {
                    "Worker": {
                    "Identity": identity,
                    "ownerAddress": account,
                    "type": "LWEXT",
                    "Host": self.extension_id
                    },
                    "Capacity": {
                    "AvailableMemory": memory,
                    "AvailableStorage": storage,
                    "AvailableGPU": "",
                    "AvailableModels": []
                    }
                },
                "msgType": "HEARTBEAT",
                "workerType": "LWEXT",
                "workerID": identity
            }

            await wss.send_json(heartbeat_message)
            return self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} Worker ID {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{self.hide_account(identity)}{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.GREEN + Style.BRIGHT}Heartbeat Message Sended{Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
            )
        except Exception as e:
            return self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Send Heartbeat Message Failed {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )

    async def load_job_data(self, wss, account, identity):
        try:
            async for msg in wss:
                if isinstance(msg, WSMessage):
                    message = json.loads(msg.data)
                    if message.get("MsgType") != "JOB":
                        response = {
                            "type": "WEBSOCKET_RESPONSE",
                            "data": message
                        }
                        await wss.send_json(response)
                        return self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Worker ID {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{self.hide_account(identity)}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Received Message:{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {message} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    elif message.get("MsgType") == "JOB":
                        response = {
                            "workerID": identity,
                            "msgType": "JOB_ASSIGNED",
                            "workerType": "LWEXT",
                            "message": {
                                "Status": True,
                                "Ref": message["UUID"]
                            }
                        }
                        await wss.send_json(response)
                        return self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Worker ID {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{self.hide_account(identity)}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Job Assigned:{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {message} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
        except Exception as e:
            return self.log(
                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Send Job Data Failed {Style.RESET_ALL}"
                f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
            )
    
    async def connect_websocket(self, account: str, token: str, use_proxy: bool, proxy=None, retries=5):
        wss_url = f"wss://apitn.openledger.xyz/ws/v1/orch?authToken={token}"
        headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Host": "apitn.openledger.xyz",
            "Origin": self.extension_id,
            "Pragma": "no-cache",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": "pyAFsQgNHYvbq16if2s6Bw==",
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        registered = False

        id = self.generate_id()
        identity = self.generate_worker_id(account)
        memory = round(random.uniform(0, 32), 2)
        storage = str(round(random.uniform(0, 500), 2))

        while True:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=60))

            try:
                for attempt in range(retries):
                    try:
                        async with session.ws_connect(wss_url, headers=headers) as wss:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                            )
                            
                            if not registered:
                                await self.send_register_msg(wss, account, id, identity)
                                registered = True

                            async def send_heartbeat():
                                while not wss.closed:
                                    await asyncio.sleep(30)
                                    await self.send_heartbeat_msg(wss, account, identity, memory, storage)

                            heartbeat_task = asyncio.create_task(send_heartbeat())

                            try:
                                await self.load_job_data(wss, account, identity)
                            except Exception as e:
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.RED + Style.BRIGHT} Websocket Communication Error {Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                                )
                            finally:
                                if not wss.closed:
                                    await wss.close()
                                heartbeat_task.cancel()
                                try:
                                    await heartbeat_task
                                except asyncio.CancelledError:
                                    pass

                    except Exception as e:
                        if attempt < retries - 1:
                            await asyncio.sleep(5)
                            continue

                        text = "Retrying..."
                        if use_proxy:
                            text = "Retrying With Next Proxy..."

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}Websocket Not Connected{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.BLUE + Style.BRIGHT}{text}{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                        if use_proxy:
                            proxy = self.get_next_proxy()

            except asyncio.CancelledError:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Websocket Is Closed {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()
        
    async def question(self):
        while True:
            try:
                print("1. Run With Auto Proxy")
                print("2. Run With Manual Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto Proxy" if choose == 1 else 
                        "With Manual Proxy" if choose == 2 else 
                        "Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
        
    async def process_accounts(self, account: str, use_proxy: bool):
        proxy = None

        if use_proxy:
            proxy = self.get_next_proxy()

        token = None
        while token is None:
            token = await self.generate_token(account, proxy)
            if not token:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Proxy {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}GET Access Token Failed{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                )

                if not use_proxy:
                    return
                
                await asyncio.sleep(1)

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Try With Next Proxy...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )

                proxy = self.get_next_proxy()
                continue

            asyncio.create_task(self.user_earning(account, token, proxy))

            check_in = await self.checkin_data(account, token, proxy)
            if check_in:
                if not check_in['claimed']:
                    claim = await self.claim_checkin(account, token, proxy)
                    if claim and claim['claimed']:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Check-In {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Is Claimed{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Reward{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {check_in['dailyPoint']} PTS {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Check-In {Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT}Isn't Claimed{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Check-In {Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT}Is Already Claimed{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {self.hide_account(account)} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} GET Check-In Data Failed {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                )
            
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Try Connect to Websocket...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(3)
        
            await self.connect_websocket(account, token, use_proxy, proxy)
    
    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            use_proxy_choice = await self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy and use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy and use_proxy_choice == 2:
                await self.load_manual_proxy()
            
            while True:
                tasks = []
                for account in accounts:
                    account = account.strip()
                    if account:
                        tasks.append(self.process_accounts(account, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(3)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = OepnLedger()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Oepn Ledger - BOT{Style.RESET_ALL}                                       "                              
        )
