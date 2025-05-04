import os, sys, heapq
from datetime import datetime
from sqlmodel import select
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import get_session
from models.order import Order
from services.tx_executor import TxExecutor
from services.quote_fetcher import QuoteFetcher
from services.path_finder import PathFinder
from services.pool_fetcher import PoolFetcher
from services.token_validator import TokenValidator
from utils.token_list import TOKENS

INFURA_URL = os.getenv("INFURA_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
SWAP_ROUTER_ADDRESS = os.getenv("SWAP_ROUTER")
UNISWAP_QUOTER_ADDRESS = os.getenv("UNISWAP_QUOTER_ADDRESS")
UNISWAP_FACTORY_ADDRESS = os.getenv("UNISWAP_FACTORY_ADDRESS")

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
tx_executor = TxExecutor(w3, SWAP_ROUTER_ADDRESS, PRIVATE_KEY)
quote_fetcher = QuoteFetcher(w3, UNISWAP_QUOTER_ADDRESS)
pool_fetcher = PoolFetcher(w3, UNISWAP_FACTORY_ADDRESS)
path_finder = PathFinder(w3, UNISWAP_FACTORY_ADDRESS)

token_list = list(TOKENS.values())
pool_data = pool_fetcher.fetch_pairs(token_list)
path_finder.build_graph(pool_data)
validator = TokenValidator(w3)

def match_orders():
    for session in get_session():
        now = datetime.utcnow()
        statement = select(Order).where(Order.status == "OPEN")
        orders = session.exec(statement).all()
        
        queue = []
        
        for order in orders:
            priority = abs(order.target_price - quote_fetcher.get_price(order.token_in, order.token_out))
            heapq.heappush(queue, (priority, order))

        while queue:
            _, order = heapq.heappop(queue)
            
            if order.expiry_time < now:
                print(f"Order {order.id} Expired")
                order.status = "expired"
                session.add(order)
                continue
            
            amount_in_wei = Web3.to_wei(order.amount_in, 'ether')
            
            if not validator.has_sufficient_balance(order.token_in, order.user_address, amount_in_wei):
                    print(f"Insufficient balance, skip order {order.id}")
                    continue
            
            best_path, amount_out = path_finder.find_best_path(
                quote_fetcher, order.token_in, order.token_out, amount_in_wei
            )
            
            if not best_path:
                print(f"No path available: {order.token_in} -> {order.token_out}")
                continue
            
            slippage_pct = order.slippage or 1.0
            min_amount_out = amount_out  * (1 - slippage_pct / 100.0)
            
            print(f"{order.id} Current Quotes: {amount_out:.6f}, Minimum expectations: {min_amount_out:.6f}")
            
            if amount_out >= min_amount_out:
                if not validator.has_sufficient_allowance(order.token_in, order.user_address, SWAP_ROUTER_ADDRESS, amount_in_wei):
                    print(f"user {order.user_address} Not authorized enough SwapRouter，Skip Order {order.id}")
                    continue
                
                try:
                    order.status = "PENDING"
                    session.add(order)
                    session.commit()

                    deadline = int(datetime.utcnow().timestamp()) + 600
                    tx_executor.execute_trade(
                        order.amount_in,
                        order.token_in,
                        order.token_out,
                        min_amount_out=min_amount_out,
                        deadline=deadline
                    )
                    order.status = "FILLED"
                    print(f"Executed Orders {order.id}")
                except Exception as e:
                    print(f"Execution failed: {e}")

            session.add(order)
        session.commit()
    print("Matching completed")
