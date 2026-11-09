# CheckPoint Shop Bot 🛒

[![Project Status](https://img.shields.io/badge/Status-Finished-blue)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-%233776AB?logo=python)](https://python.org/)
[![Telegram](https://img.shields.io/badge/Telegram_Bot_API-4.23.0-%2326A5E4?logo=telegram)](https://core.telegram.org/bots/api)

Telegram bot for a shop's ordering and delivery: customers browse the catalog and order products delivered to their room. Features role-based access, payment processing, and real-time order tracking.

---

## ✨ Core Features
- **Role System**:
    - 👤 Customer registration with delivery details
    - 👨‍💼 Admin panel for inventory/order management
- **Shopping Experience**:
    - 🛍️ Product catalog browsing with intuitive navigation
    - 📦 Order creation with quantity selection
    - 🏠 Delivery to the customer's room
- **Payment & Tracking**:
    - 💳 Screenshot-based payment confirmation
    - 📊 Real-time order status updates
    - 🔄 Admin order processing workflow

---

## 🧰 Tech Stack
- **Backend**: 
  ![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python)
  ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.36-1C1C1C?logo=python)
- **Database**: 
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16.3-4169E1?logo=postgresql)
  ![psycopg2](https://img.shields.io/badge/psycopg2-2.9.10-1C1C1C)
- **Telegram Integration**: 
  ![pyTelegramBotAPI](https://img.shields.io/badge/pyTelegramBotAPI-4.23.0-26A5E4?logo=telegram)

---

## ⚙️ Installation & Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/Zebaro24/Check-Point-SHOP.git
   cd checkpoint-shop-bot
   ```

2. **Configure environment**  
   Create `.env` file:
   ```env
   DATABASE_URL=postgres://user:password@localhost:5432/shop_db
   TELEGRAM_TOKEN=your_bot_token_here
   ```

3. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python database.py
   ```

---

## 🚀 Launching the Bot

```bash
python runner.py
```

### Client Flow
1. Start bot with `/start` command
2. Register with room number
3. Browse products → Select items → Confirm payment
4. Track order status in real-time

### Admin Flow
1. Access admin panel (pre-configured accounts)
2. Manage product inventory
3. Process orders: Confirm payments → Update statuses → Track deliveries

---

## 🗂️ Project Structure
```bash
handlers/
├── admin_handler.py    # Admin commands processing
├── client_handler.py   # Customer interactions
└── base_handler.py     # Core handler logic
db_orm/
├── product.py          # Product data model
├── order.py            # Order management
└── roles.py            # User role definitions
config.py               # Environment configuration
database.py             # DB connection manager
telegram_bot.py         # Bot entry point
```

---

## 📸 Interface Preview
| Customer View | Admin Panel |
|--------------|-------------|
| <img src="https://github.com/user-attachments/assets/bd9f2255-8290-4d50-82fb-b9272e94073c" alt="Customer UI" width="400" /> | <img src="https://github.com/user-attachments/assets/e95855d3-b914-48f2-8c0b-14d3502c8bab" alt="Admin UI" width="400" /> |
| <img src="https://github.com/user-attachments/assets/33c26dbc-9b02-4df7-9885-54f5c695f56e" alt="Progress" width="400" /> | <img src="https://github.com/user-attachments/assets/b6e8df7a-33d1-4980-8e72-8d4c1cd83894" alt="Manage" width="400" /> |

---

## 📬 Contact
- **Developer**: Denys Shcherbatyi
- **Email**: zebaro.work@gmail.com
