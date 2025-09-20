# TG-DDOS-UDP

![License](https://img.shields.io/badge/license-MIT-green)  
![Version](https://img.shields.io/badge/version-1.1.0-orange)  

A Telegram bot for managing & performing DDOS operations and added user access via redeem codes. Built with Python and integrated with MongoDB for user management and code redemption.

> ⚠️ **Disclaimer:** This project is intended for educational purposes only. Unauthorized attacks on servers or networks are illegal and can lead to severe consequences. Only use this bot on systems you own or have explicit permission to test.

> ✅ Supported on **Windows**, **Linux**, **Mac** and other major operating systems.

---

## Features

- ✅ User authentication with expiry-based access.
- ⚡ Admin-only commands to manage users and generate redeem codes.
- 🚀 Attack (via external script `kratos`).
- 💳 Redeem code system with expiry and max usage limits.
- 👥 List all active users and their expiry statuses.
- 📈 Cooldown tracking to prevent repeated attacks (abuse).

---

## Requirements

- Python 3.10+
- `python-telegram-bot`
- `pymongo`
- MongoDB database

Install dependencies:

```bash
pip install -r requirements.txt
