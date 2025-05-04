from web3 import Web3
from collections import defaultdict
import heapq

from utils.token_list import TOKENS

token_addresses = list(TOKENS.values())

class PathFinder:
    def __init__(self, w3: Web3, factory_address: str, fee_list=[500, 3000, 10000]):
        self.w3 = w3
        self.factory = w3.eth.contract(address=Web3.to_checksum_address(factory_address), abi=[{
            "inputs": [
                {"internalType": "address", "name": "tokenA", "type": "address"},
                {"internalType": "address", "name": "tokenB", "type": "address"},
                {"internalType": "uint24", "name": "fee", "type": "uint24"}
            ],
            "name": "getPool",
            "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        }])
        self.fee_list = fee_list
        self.graph = defaultdict(list)

    def build_graph(self, pool_data):
        for pool in pool_data:
            try:
                tokenA = Web3.to_checksum_address(pool['token0'])
                tokenB = Web3.to_checksum_address(pool['token1'])
                fee = pool['fee']
                t0 = tokenA.lower()
                t1 = tokenB.lower()
                self.graph[t0].append((t1, fee))
                self.graph[t1].append((t0, fee))
            except Exception as e:
                print(f"Error adding pool to graph for {pool}: {e}")

    def heuristic(self, token_a, token_b):
        """A* Heuristic function, currently using Dijkstra algorithm, which is always 0"""
        return 0
    
    
    def find_all_paths(self, start: str, goal: str, max_hops=3) -> list[list[str]]:
        start = start.lower()
        goal = goal.lower()
        paths = []

        def dfs(current, path, visited):
            if len(path) > max_hops + 1:
                return
            if current == goal:
                paths.append(path[:])
                return
            for neighbor, _ in self.graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    dfs(neighbor, path, visited)
                    path.pop()
                    visited.remove(neighbor)

        dfs(start, [start], set([start]))
        return paths
    
    def find_best_path(self, quote_fetcher, token_in: str, token_out: str, amount_in_wei: int):
        all_paths = self.find_all_paths(token_in, token_out)
        best_path = None
        best_amount_out = 0

        for path in all_paths:
            try:
                amount_out = quote_fetcher.get_path_quote(path, amount_in_wei)
                if amount_out > best_amount_out:
                    best_path = path
                    best_amount_out = amount_out
            except Exception as e:
                print(f"Failed to quote: {path}, error: {e}")
                continue

        return best_path, best_amount_out

    def find_path(self, start, goal):
        start = start.lower()
        goal = goal.lower()

        open_set = [(0, start, [])]  # cost, current_token, path
        visited = set()

        while open_set:
            cost, current, path = heapq.heappop(open_set)
            if current in visited:
                continue
            visited.add(current)

            path = path + [current]
            if current == goal:
                return path

            for neighbor, fee in self.graph[current]:
                if neighbor not in visited:
                    total_cost = cost + fee + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (total_cost, neighbor, path))

        return None
