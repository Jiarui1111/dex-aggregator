# 🦄 DEX Aggregator (Uniswap V3)

A full-stack decentralized exchange aggregator based on Uniswap V3.  
This project provides limit order creation, optimal path routing, token validation, and quote fetching using Ethereum smart contracts.

---

## 📁 Project Structure

DEX_AGGREGATOR/
│
├── abis/ # ABI files for Uniswap V3 and ERC20 contracts
│ ├── erc20.json
│ ├── quoter.json
│ ├── uniswap_factory_abi.json
│ ├── uniswap_v3_factory.json
│ └── uniswap_v3_pool.json
│
├── db/ # Database session management
│ └── session.py
│
├── models/ # SQLModel/Pydantic data models
│ ├── enums.py
│ └── order.py
│
├── routes/ # FastAPI route definitions
│ └── orders.py
│
├── services/ # Core logic and smart contract interactions
│ ├── order_matcher.py
│ ├── path_finder.py
│ ├── pool_fetcher.py
│ ├── price_checker.py
│ ├── quote_fetcher.py
│ ├── token_validator.py
│ ├── tx_executor.py
│ └── uniswap_v3_pool.py
│
├── tasks/ # (Optional) Scheduled jobs or background tasks
│
├── utils/ # Utility functions
│ └── token_list.py
│
├── .env # Environment variables (not committed)
├── dex.db # Local SQLite database
├── fix_database.py # Database migration or fixing script
└── README.md
---

## 🚀 Features

- 🔁 **Limit Order Engine** — Create and manage on-chain style limit orders
- 🔍 **Optimal Path Routing** — Find best swap paths using Uniswap V3 pool data
- 💬 **Quote Fetcher** — Interact with Uniswap’s `Quoter` contract
- 🧪 **Token Validator** — Check balances and allowances before swap
- 🔗 **Modular Service Layer** — Clean separation of pool fetching, routing, price quoting, and execution logic

---

## ⚙️ Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
