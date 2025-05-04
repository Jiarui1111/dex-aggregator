# DEX Aggregator (Uniswap V3)

A decentralized exchange aggregator based on Uniswap V3.  
This project supports limit order creation, optimal routing via Dijkstra search, on-chain quote fetching, and swap execution — all in a modular FastAPI backend.

---

## 已完成关键功能

| 模块 | 状态 | 说明 |
|------|------|------|
| 架构设计 | ✔️ | `FastAPI + SQLite + APScheduler + Web3` |
| 限价单下单接口 | ✔️ | `POST /orders/limit` 创建订单并存储到数据库 |
| 状态管理 | ✔️ | 支持 `OPEN → PENDING → FILLED / CANCELLED / EXPIRED` 状态流转 |
| 状态切换逻辑 | ✔️ | 执行订单前标记为 `PENDING`，防止并发重复撮合 |
| Uniswap V3 swap | ✔️ | 使用 `swapExactTokensForTokens` 执行真实交易 |
| 报价系统 | ✔️ | `QuoteFetcher` 调用 `quoteExactInputSingle` 获取报价 |
| 路径搜索 | ✔️ | `PathFinder` 使用 Dijkstra 算法，支持多 fee tier |
| 多池路由报价 | ✔️ | 遍历所有路径，选择 `amountOut` 最大者 |
| 定时执行模块 | ✔️ | `APScheduler` 定时调用 `order_matcher.py` |
| 滑点控制 | ✔️ | `min_amount_out = price * (1 - slippage%)` |
| 取消订单接口 | ✔️ | `/orders/{id}/cancel` 设置状态为 `CANCELLED` |

---

安装依赖
```bash
pip install -r requirements.txt
```
启动服务
```bash
uvicorn main:app --reload
``` 


```
以下是本项目实现过程中使用的文档与源码参考：

Uniswap 官方 GitHub 仓库：
🔗 https://github.com/Uniswap

高级指南：池子数据提取（SDK v3）：
🔗 https://docs.uniswap.org/sdk/v3/guides/advanced/pool-data

智能合约接口文档：IUniswapV3PoolState：
🔗 https://docs.uniswap.org/contracts/v3/reference/core/interfaces/pool/IUniswapV3PoolState

Uniswap V3 部署地址（主网 / L2）：
🔗 https://docs.uniswap.org/contracts/v3/reference/deployments/ethereum-deployments

Uniswap V3 Factory 合约源码：
🔗 https://github.com/Uniswap/v3-core/blob/v1.0.0/contracts/UniswapV3Factory.sol

非官方 Uniswap V3 中文手册（用户界面相关）：
🔗 https://uniswapv3book.com/milestone_4/user-interface.html
```
