import os, sys, time
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.pool_fetcher import PoolFetcher
from services.path_finder import PathFinder

POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"name": "sqrtPriceX96", "type": "uint160"},
            {"name": "tick", "type": "int24"},
            {"name": "observationIndex", "type": "uint16"},
            {"name": "observationCardinality", "type": "uint16"},
            {"name": "observationCardinalityNext", "type": "uint16"},
            {"name": "feeProtocol", "type": "uint8"},
            {"name": "unlocked", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMin", "type": "uint256"},
            {"name": "path", "type": "address[]"},
            {"name": "to", "type": "address"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

FACTORY_ADDRESS = os.getenv("UNISWAP_FACTORY_ADDRESS")  


class TxExecutor:
    def __init__(self, w3: Web3, contract_address: str, private_key: str):
        self.w3 = w3
        self.private_key = private_key
        self.contract_address = contract_address
        
        self.account = self.w3.eth.account.from_key(private_key)
    
    def build_transaction(self, function, *args):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        tx = function(*args).build_transaction({
            'gas': 2000000,
            'gasPrice': self.w3.to_wei('20', 'gwei'),
            'nonce': nonce,
            'chainId': 1  
        })
        return tx

    def sign_transaction(self, tx):
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        return signed_tx
    
    def send_transaction(self, signed_tx):
        try:
            print(signed_tx.raw_transaction.hex())
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction.hex())
            return tx_hash
        except Exception as e:
            print(f"Error sending transaction: {e}")
            return None

    def wait_for_receipt(self, tx_hash, timeout=120):
        try:
            start_time = time.time()
            while True:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    return receipt
                elif time.time() - start_time > timeout:
                    print("Transaction timeout.")
                    return None
                time.sleep(5)
        except Exception as e:
            print(f"Error waiting for transaction receipt: {e}")
            return None

    def execute_trade(self, amount_in, token_in, token_out, min_amount_out, deadline):
        token_list = [token_in, token_out, "0x6B175474E89094C44Da98b954EedeAC495271d0F"] 
        fetcher = PoolFetcher(self.w3, FACTORY_ADDRESS)
        pool_data = fetcher.fetch_pairs(token_list)
        path_finder = PathFinder(self.w3, FACTORY_ADDRESS)
        path_finder.build_graph(pool_data) 
        path = path_finder.find_path(token_in, token_out)   

        if not path:
            print("No path found.")
            return
        print(path)
        amount_in = Web3.to_wei(amount_in, 'ether')
        min_amount_out = Web3.to_wei(min_amount_out, 'ether')
        
        token_in = Web3.to_checksum_address(token_in)
        token_out = Web3.to_checksum_address(token_out)
        
        uniswap_contract = self.w3.eth.contract(address=self.contract_address, abi=POOL_ABI)
        function = uniswap_contract.functions.swapExactTokensForTokens(
            amount_in,
            min_amount_out,  
            # [token_in, token_out],  
            path,    
            self.account.address,
            deadline
        )
        
        tx = self.build_transaction(function, amount_in, min_amount_out, [token_in, token_out], self.account.address, deadline)
        signed_tx = self.sign_transaction(tx)   
        tx_hash = self.send_transaction(signed_tx)
        
        if tx_hash:
            print(f"Transaction hash: {tx_hash.hex()}")
            receipt = self.wait_for_receipt(tx_hash)
            if receipt:
                print("Transaction executed successfully!")
            else:
                print("Transaction failed or timed out.")
        else:
            print("Transaction failed to send.")
