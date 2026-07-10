# AniToon Bot

A production-ready Telegram File Manager built with **Pyrofork**, **Motor (MongoDB)**, **FFmpeg**, and **asyncio**.

## Features

* Rename any Telegram file
* Video quality conversion
* Format conversion
* Compression
* Audio extraction
* Automatic thumbnails
* Custom thumbnails
* Caption templates
* Batch processing
* Queue system
* Pause / Resume / Cancel
* Premium users
* Force Subscribe
* File Index
* Search
* Broadcast
* Statistics
* Admin Panel
* Auto Join Request Acceptor
* Auto Reactions
* Multiple Downloader Support
* Docker Support
* Render Support
* Railway Support
* Koyeb Support

---

# Requirements

* Python 3.11+
* MongoDB Atlas
* FFmpeg
* Telegram Bot Token
* Telegram API ID
* Telegram API Hash

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd AniToonBot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials.

Run the bot:

```bash
python -m main
```

---

# Docker

Build:

```bash
docker build -t anitoon-bot .
```

Run:

```bash
docker run --env-file .env -p 10000:10000 anitoon-bot
```

---

# Render

1. Push the project to GitHub.
2. Create a new **Web Service** on Render.
3. Connect your repository.
4. Render will detect `render.yaml`.
5. Add the required environment variables.
6. Deploy.

---

# Environment Variables

Required:

* API_ID
* API_HASH
* BOT_TOKEN
* MONGO_URI

Optional:

* DATABASE_NAME
* BOT_OWNER
* BOT_USERNAME
* LOG_LEVEL
* PORT

See `.env.example` for the full list.

---

# Project Structure

```
bot/
├── main.py
├── bot.py
├── config.py
├── database.py
├── logger.py
├── web.py
├── handlers/
├── plugins/
├── helpers/
├── ffmpeg/
├── downloader/
├── uploader/
├── queue/
├── middleware/
├── admin/
├── database/
├── settings/
├── utils/
├── cache/
├── temp/
└── logs/
```

---

# License

MIT License.
