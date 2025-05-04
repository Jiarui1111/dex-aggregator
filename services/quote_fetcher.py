import os, json
from web3 import Web3

class QuoteFetcher:
    def __init__(self, w3: Web3, quoter_address: str):
        self.w3 = w3
        abi_path = os.path.join(os.path.dirname(__file__), "..", "abis", "quoter.json")
        with open(abi_path, "r") as f:
            QUOTER_ABI = json.load(f)
        self.contract = w3.eth.contract(
            address=Web3.to_checksum_address(quoter_address),
            abi=QUOTER_ABI
        )

    def get_price(self, token_in: str, token_out: str, fee: int = 3000, amount_in_wei: int = Web3.to_wei(1, 'ether')) -> float:
        try:
            amount_out = self.contract.functions.quoteExactInputSingle(
                Web3.to_checksum_address(token_in),
                Web3.to_checksum_address(token_out),
                fee,
                amount_in_wei,
                0
            ).call()

            return Web3.from_wei(amount_out, 'ether')  
        except Exception as e:
            print(f"Failed to quote: {e}")
            return 0
        
        
    def get_path_quote(self, path: list[str], amount_in_wei: int) -> int:
        if len(path) == 2:
            return self.get_price(path[0], path[1], fee=3000, amount_in_wei=amount_in_wei)
        else:
            raise NotImplementedError("Currently only single-hop path quotation is supported")
        
