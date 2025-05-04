import json 
from web3 import Web3

class UniswapV3Pool:
    def __init__(self, infura_url: str, factory_address: str):
        self.w3 = Web3(Web3.HTTPProvider(infura_url))
        
        self.factory_address = Web3.to_checksum_address(factory_address)

       
        with open("uniswap_factory_abi.json", "r") as f:
            self.factory_abi = json.load(f)
        
        self.factory_contract = self.w3.eth.contract(address=self.factory_address, abi=self.factory_abi)

    def get_pool_address(self, token_a: str, token_b: str, fee: int) -> str:
        token_a = Web3.to_checksum_address(token_a)
        token_b = Web3.to_checksum_address(token_b)
        
        try:
            pool_address = self.factory_contract.functions.getPool(token_a, token_b, fee).call()
            if pool_address == "0x0000000000000000000000000000000000000000":
                print("No pool found for this pair!")
            else:
                print(f"Pool address: {pool_address}")
            return pool_address
        except Exception as e:
            print(f"Error: {e}")
            return None