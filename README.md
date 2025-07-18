# CheckPoint Shop Bot 🛒

[![Project Status](https://img.shields.io/badge/Status-Finished-blue)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-%233776AB?logo=python)](https://python.org/)
[![Telegram](https://img.shields.io/badge/Telegram_Bot_API-4.23.0-%2326A5E4?logo=telegram)](https://core.telegram.org/bots/api)

Telegram bot for university shop operations, enabling students to order products with dormitory delivery. Features role-based access, payment processing, and real-time order tracking.

---

## ✨ Core Features
- **Role System**:
    - 👤 Student registration with room details
    - 👨‍💼 Admin panel for inventory/order management
- **Shopping Experience**:
    - 🛍️ Product catalog browsing with intuitive navigation
    - 📦 Order creation with quantity selection
    - 🏠 Dormitory room delivery
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
   git clone https://github.com/username/checkpoint-shop-bot.git
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
python telegram_bot.py
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
├── client_handler.py   # Student interactions
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
| Student View | Admin Panel |
|--------------|-------------|
| ![Student UI](https://placehold.co/300x150/3d5a80/ffffff?text=Student+Dashboard) | ![Admin UI](https://placehold.co/300x150/293241/ffffff?text=Admin+Dashboard) |
| ![Flow](https://placehold.co/300x150/98c1d9/000000?text=Course+Progress) | ![Management](https://placehold.co/300x150/ee6c4d/ffffff?text=User+Management) |


---

## 📬 Contact
- **Developer**: Denys Shcherbatyi
- **Email**: zebaro.work@gmail.com
- **GitHub**: [github.com/Zebaro24](https://github.com/Zebaro24)