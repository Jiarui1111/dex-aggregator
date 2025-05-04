import os, sys, time, json
from web3 import Web3
from apscheduler.schedulers.background import BackgroundScheduler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.uniswap_v3_pool import UniswapV3Pool
from services.tx_executor import TxExecutor
from utils.token_list import TOKENS


INFURA_URL = "https://mainnet.infura.io/v3/259cbfedd34247f9beeb96d0315408ca"
# INFURA_URL = "https://sepolia.infura.io/v3/259cbfedd34247f9beeb96d0315408ca"
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
UNISWAP_FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31F984"  
# 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f 
token_addresses = list(TOKENS.values())
if w3.is_connected():
    print("Connected to Ethereum network via Infura!")
else:
    print("Failed to connect.")

uniswap_pool = UniswapV3Pool(INFURA_URL, UNISWAP_FACTORY_ADDRESS)

# The addresses of Token A and Token B (e.g. USDC and WETH)
token_a = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"  
token_b = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" 
fee = 3000  

UNISWAP_POOL_ADDRESS = uniswap_pool.get_pool_address(token_a, token_b, fee)


with open("abis/uniswap_v3_pool.json") as f:
    POOL_ABI = json.load(f)

uniswap_contract = w3.eth.contract(address=UNISWAP_POOL_ADDRESS, abi=POOL_ABI)


def get_current_tick(contract):
    try:
        slot0_data = contract.functions.slot0().call()
        
        print(f"Raw slot0 data: {slot0_data}")
        
        tick = slot0_data[1]  
        
        print(f"Tick: {tick}")
        return tick
    except Exception as e:
        print(f"Error while fetching tick: {e}")
        return None

def check_price():
    uniswap_tick = get_current_tick(uniswap_contract)
    print(f"Current Uniswap V3 tick: {uniswap_tick}")
    
    target_tick = 5000
    
    if uniswap_tick >= target_tick:
        print(f"Price reached! Triggering execution.")
        
        amount_in = Web3.to_wei(1, 'ether')  
        token_in = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"  
        token_out = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"  
        min_amount_out = Web3.to_wei(0.95, 'ether')  
        deadline = int(time.time()) + 3600  
        
        private_key = "9a2c2e0091253a49ff3ce9976fa2e090887778b595f04517909cda0029c8863c"  
        tx_executor = TxExecutor(w3, UNISWAP_POOL_ADDRESS, private_key)
        tx_executor.execute_trade(amount_in, token_in, token_out, min_amount_out, deadline)
    else:
        print("Price hasn't reached the target yet.")

scheduler = BackgroundScheduler()
scheduler.add_job(check_price, 'interval', minutes=1)
scheduler.start()

try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
