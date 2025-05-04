import os, json
from web3 import Web3

class PoolFetcher:
    def __init__(self, w3: Web3, factory_address: str):
        self.w3 = w3
        abi_path = os.path.join(os.path.dirname(__file__), "..", "abis", "uniswap_v3_factory.json")
        with open(abi_path, "r") as f:
            factory_abi = json.load(f)

        self.factory = w3.eth.contract(address=Web3.to_checksum_address(factory_address), abi=factory_abi)
        self.fee_tiers = [500, 3000, 10000]

    def fetch_pairs(self, tokens: list[str]):
        pools = []
        for i in range(len(tokens)):
            for j in range(i + 1, len(tokens)):
                tokenA = Web3.to_checksum_address(tokens[i])
                tokenB = Web3.to_checksum_address(tokens[j])
                for fee in self.fee_tiers:
                    pool = self.factory.functions.getPool(tokenA, tokenB, fee).call()
                    if pool and pool != '0x0000000000000000000000000000000000000000':
                        pools.append({
                            'token0': tokens[i],
                            'token1': tokens[j],
                            'fee': fee,
                            'pool': pool
                        })
        return pools
