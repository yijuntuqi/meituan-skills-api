# 美团 Skills API Gateway

> 将美团官方开放的 3 个 AI Skill（酒旅 / 领券 / 跑腿下单）统一封装为 **HTTP API**，本地部署后可被任意项目（Web 应用、Agent、自动化脚本）直接调用。

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 为什么需要这个项目

美团技术开放平台（[developer.meituan.com](https://developer.meituan.com)）以 **Skill** 形式开放了酒旅查询、跑腿下单等能力，但官方提供的调用方式是 CLI 脚本 / Node 包：

- `npx @meituan-travel/ht-ai query ...`（酒旅，耗时 1-2 分钟）
- `node paotui.js preview_and_submit ...`（跑腿，参数是复杂 JSON）
- `python auth.py send-sms ...`（领券，多步短信登录）

直接在业务项目里拼装子进程、处理超时/鉴权/异步任务非常繁琐。本项目在它们之上封装了一层**统一的 REST API**：

- 一次部署，多个项目复用，语言无关
- 统一 `X-API-Key` 鉴权、统一错误结构、自动 Swagger 文档
- 酒旅长查询自动转为「提交任务 → 轮询结果」异步模式
- 自动处理 Windows 下 `npx.cmd`、中文编码、子进程超时等坑

## 功能与接口

**统一请求头**：`X-API-Key: <你的密钥>`（健康检查除外）

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 系统 | GET | `/health` | 健康检查（免鉴权） |
| 酒旅 | POST | `/api/travel/query` | 提交酒旅查询（异步，返回 `task_id`） |
| 酒旅 | GET | `/api/travel/result/{task_id}` | 轮询查询结果 |
| 领券 | GET | `/api/coupon/auth/status` | 查看本地美团登录状态 |
| 领券 | POST | `/api/coupon/auth/send-sms` | 发送短信验证码 |
| 领券 | POST | `/api/coupon/auth/verify` | 验证码登录 |
| 领券 | POST | `/api/coupon/auth/logout` | 退出登录 |
| 领券 | POST | `/api/coupon/issue` | 一键领取美团专属红包券 |
| 跑腿 | GET | `/api/paotui/auth/status` | 检查跑腿授权状态 |
| 跑腿 | POST | `/api/paotui/poi/search` | POI 地址搜索 |
| 跑腿 | GET | `/api/paotui/address-list` | 获取美团地址簿 |
| 跑腿 | POST | `/api/paotui/order/preview` | 订单预览（**不会**下单） |
| 跑腿 | POST | `/api/paotui/order/submit` | 确认提交订单（**真实下单**） |
| 跑腿 | GET | `/api/paotui/order/{order_id}` | 查询订单状态 |

启动后访问交互式文档：**http://127.0.0.1:8000/docs**

### 典型调用示例

酒旅查询（异步）：

```bash
# 1. 提交，拿到 task_id
curl -X POST http://127.0.0.1:8000/api/travel/query \
  -H "X-API-Key: your-key" -H "Content-Type: application/json" \
  -d '{"query":"本周末北京情侣酒店，预算500内","city":"北京"}'

# 2. 约 1-2 分钟后轮询
curl http://127.0.0.1:8000/api/travel/result/<task_id> -H "X-API-Key: your-key"
```

领券（短信登录后一键领）：

```bash
curl -X POST http://127.0.0.1:8000/api/coupon/auth/send-sms \
  -H "X-API-Key: your-key" -H "Content-Type: application/json" \
  -d '{"phone":"13800000000"}'

curl -X POST http://127.0.0.1:8000/api/coupon/auth/verify \
  -H "X-API-Key: your-key" -H "Content-Type: application/json" \
  -d '{"phone":"13800000000","code":"123456"}'

curl -X POST http://127.0.0.1:8000/api/coupon/issue -H "X-API-Key: your-key"
```

跑腿也支持通过请求头 `X-Access-Token` 动态传入用户 passport token（不落地到服务端配置）。

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+（酒旅用 `npx`、跑腿用 `node`）
- 前往 [美团开发者中心](https://developer.meituan.com/zh/v2/dev/token) 申请酒旅 API Token

### 安装与启动

```bash
git clone git@github.com:yijuntuqi/meituan-skills-api.git
cd meituan-skills-api

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env       # Windows: copy .env.example .env
# 编辑 .env，至少填入 API_KEY 和 MEITUAN_HT_TOKEN

python run.py
```

打开 http://127.0.0.1:8000/docs 即可调试。

### 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `API_KEY` | 是 | 调用方请求头 `X-API-Key` 的值，自己设一个强随机串 |
| `MEITUAN_HT_TOKEN` | 酒旅必填 | 美团酒旅 Skill Token |
| `MCP_ACCESS_TOKEN` | 否 | 跑腿 passport token，也可由 `X-Access-Token` 按请求传入 |
| `MEITUAN_PAOTUI_SOURCE_FROM` | 否 | 渠道标识，默认 `aihub` |
| `COUPON_PYTHON` | 否 | 领券脚本使用的 Python 解释器，默认 `python` |
| `TRAVEL_TIMEOUT` / `PAOTUI_TIMEOUT` / `COUPON_TIMEOUT` | 否 | 各 Skill 子进程超时秒数 |

## 架构

```
调用方 (Web / Agent / 脚本)
        │  HTTP + X-API-Key
        ▼
┌─────────────────────────────┐
│  FastAPI (app/main.py)       │
│  ├─ routers/   请求校验与路由 │
│  ├─ skills/    子进程封装层   │  ── npx ht-ai      (酒旅)
│  └─ task_store 异步任务表     │  ── node paotui.js (跑腿)
└─────────────────────────────┘    ── python auth/issue (领券)
        │
        ▼
skills/  ← 美团官方 Skill 原样存放，未做修改
```

- **零侵入**：官方 Skill 文件原样存放在 `skills/`，升级时直接替换目录即可
- **凭证安全**：`.env` 与本地美团登录凭证（`~/.xiaomei-workspace/`）已被 `.gitignore` 排除，不会进仓库

## 项目结构

```
meituan-skills-api/
├── app/
│   ├── main.py          # FastAPI 入口
│   ├── config.py        # 环境变量配置
│   ├── auth.py          # API Key 校验
│   ├── task_store.py    # 异步任务内存存储
│   ├── skills/          # 三个 Skill 的子进程封装
│   └── routers/         # HTTP 路由
├── skills/              # 美团官方 Skill（原样）
├── .env.example
├── requirements.txt
└── run.py
```

## 安全须知

1. 本服务默认无账号体系，**仅建议本地 / 内网部署**，不要直接暴露到公网
2. 跑腿 `order/submit` 是**真实消费、不可逆操作**，调用方必须先预览并让用户二次确认
3. 领券手机号、短信验证码、token 仅保存在本机，不会上传到任何第三方
4. 不要把填好密钥的 `.env` 提交到任何仓库

## 免责声明

本项目仅为美团官方 Skill 的第三方 HTTP 封装，所有数据与交易能力归美团所有；接口可能随美团官方调整而变化，使用请遵守美团开放平台协议与当地法律法规。因调用产生的真实交易由使用者自行承担。

## License

MIT
