# Starz Promosyon

A simple Telegram-native promotion hub built with Python 3.12 and aiogram 3.x.

## Exactly 3 user functions

1. **Promotions** — browse promotion information directly in Telegram.
2. **Updates** — read Starz updates directly in Telegram.
3. **Submit Promotion** — send promotion text, validate it, save it to SQLite and receive a reference number.

The bot does not use an external website as its primary user flow.

## Commands

- `/start` — open the main menu; Telegram deep-link parameters are safely accepted.
- `/help` — explain the three functions and navigation.

## Environment

Required: `BOT_TOKEN`

Optional: `ADMIN_ID`, `DATABASE_PATH`

Example values are provided in `.env.example`. Never commit real credentials.

## Run

```bash
pip install -r requirements.txt
python -m app.main
```

## Render

Build command: `pip install -r requirements.txt`

Start command: `python -m app.main`

The included `render.yaml` configures a Background Worker with a persistent `/data` disk for SQLite.

## QA

CI checks Python compilation, dispatcher construction, callback validation, content completeness and SQLite persistence.

Before advertising, manually verify the live bot with `/start`, `/start campaign123`, `/help`, every promotion/update item, valid and invalid submissions, Run Again, Back, Main Menu and repeated navigation.

Replace the example promotion/update content with real current content before commercial use. Advertise only functionality that the bot actually provides.
