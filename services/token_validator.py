import os, json
from web3 import Web3


class TokenValidator:
    def __init__(self, w3: Web3):
        self.w3 = w3
        abi_path = os.path.join(os.path.dirname(__file__), "..", "abis", "erc20.json")
        with open(abi_path, "r") as f:
            self.erc20_abi = json.load(f)

    def has_sufficient_balance(self, token_address: str, user_address: str, amount_wei: int) -> bool:
        token = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=self.erc20_abi)
        balance = token.functions.balanceOf(Web3.to_checksum_address(user_address)).call()
        return balance >= amount_wei

    def has_sufficient_allowance(self, token_address: str, user_address: str, router_address: str, amount_wei: int) -> bool:
        token = self.w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=self.erc20_abi)
        allowance = token.functions.allowance(
            Web3.to_checksum_address(user_address),
            Web3.to_checksum_address(router_address)
        ).call()
        return allowance >= amount_wei
