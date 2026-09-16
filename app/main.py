from __future__ import annotations

import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, CallbackQuery, ErrorEvent, Message

from app.config import Settings
from app.content import Item, PROMOTIONS, UPDATES
from app.keyboards import detail_menu, item_menu, main_menu, result_menu, submit_menu
from app.storage import Storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("starz_promosyon")


class SubmitState(StatesGroup):
    waiting_for_text = State()


def home_text() -> str:
    return (
        "🌟 <b>Starz Promosyon</b>\n\n"
        "A Telegram-native promotion hub. Everything you need is available directly in this chat.\n\n"
        "<b>Choose one of the 3 functions:</b>\n"
        "📢 Promotions — browse promotion information\n"
        "📰 Updates — read current in-app updates\n"
        "✍️ Submit Promotion — send a promotion for consideration"
    )


def help_text() -> str:
    return (
        "ℹ️ <b>Help</b>\n\n"
        "Starz Promosyon has exactly three user functions.\n\n"
        "📢 <b>Promotions:</b> choose an item and read its details.\n"
        "📰 <b>Updates:</b> choose an update and read it in the chat.\n"
        "✍️ <b>Submit Promotion:</b> send clear promotion text and receive a reference number.\n\n"
        "Use /start or Main Menu at any time to return home."
    )


def list_text(title: str, items: tuple[Item, ...]) -> str:
    lines = [f"<b>{title}</b>", "", "Choose an item to view its details:"]
    lines.extend(f"{i}. {item.title}" for i, item in enumerate(items, 1))
    return "\n".join(lines)


def item_text(item: Item, index: int, total: int) -> str:
    return f"<b>{item.title}</b>\n\n{item.body}\n\n<i>Item {index + 1} of {total}</i>"


def _safe_index(callback_data: str | None, prefix: str, count: int) -> int | None:
    if not callback_data or not callback_data.startswith(f"{prefix}:"):
        return None
    try:
        index = int(callback_data.split(":", 1)[1])
    except (TypeError, ValueError):
        return None
    return index if 0 <= index < count else None


async def _edit_home(callback: CallbackQuery) -> None:
    if callback.message:
        await callback.message.edit_text(home_text(), reply_markup=main_menu(), parse_mode="HTML")


def build_dispatcher(storage: Storage, settings: Settings) -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def start(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(home_text(), reply_markup=main_menu(), parse_mode="HTML")

    @dp.message(Command("help"))
    async def help_command(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer(help_text(), reply_markup=main_menu(), parse_mode="HTML")

    @dp.callback_query(F.data == "home")
    async def home(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.answer()
        await _edit_home(callback)

    @dp.callback_query(F.data == "promotions")
    async def promotions(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.answer()
        if callback.message:
            await callback.message.edit_text(list_text("📢 Promotions", PROMOTIONS), reply_markup=item_menu("promotion", len(PROMOTIONS)), parse_mode="HTML")

    @dp.callback_query(F.data.startswith("promotion:"))
    async def promotion_item(callback: CallbackQuery) -> None:
        index = _safe_index(callback.data, "promotion", len(PROMOTIONS))
        if index is None:
            await callback.answer("That option is no longer available.", show_alert=True)
            return
        await callback.answer()
        if callback.message:
            await callback.message.edit_text(item_text(PROMOTIONS[index], index, len(PROMOTIONS)), reply_markup=detail_menu("promotions"), parse_mode="HTML")

    @dp.callback_query(F.data == "updates")
    async def updates(callback: CallbackQuery, state: FSMContext) -> None:
        await state.clear()
        await callback.answer()
        if callback.message:
            await callback.message.edit_text(list_text("📰 Updates", UPDATES), reply_markup=item_menu("update", len(UPDATES)), parse_mode="HTML")

    @dp.callback_query(F.data.startswith("update:"))
    async def update_item(callback: CallbackQuery) -> None:
        index = _safe_index(callback.data, "update", len(UPDATES))
        if index is None:
            await callback.answer("That option is no longer available.", show_alert=True)
            return
        await callback.answer()
        if callback.message:
            await callback.message.edit_text(item_text(UPDATES[index], index, len(UPDATES)), reply_markup=detail_menu("updates"), parse_mode="HTML")

    @dp.callback_query(F.data == "submit")
    async def submit(callback: CallbackQuery, state: FSMContext) -> None:
        await state.set_state(SubmitState.waiting_for_text)
        await callback.answer()
        if callback.message:
            await callback.message.edit_text(
                "✍️ <b>Submit Promotion</b>\n\n"
                "Send the promotion text you want to submit.\n\n"
                "Maximum length: 1,000 characters. Keep it clear and useful. "
                "Do not send passwords, payment credentials or other private information.",
                reply_markup=submit_menu(),
                parse_mode="HTML",
            )

    @dp.message(SubmitState.waiting_for_text)
    async def receive_submission(message: Message, state: FSMContext) -> None:
        text = (message.text or "").strip()
        if not text:
            await message.answer("That input isn't valid. Please send the promotion as text.", reply_markup=submit_menu())
            return
        if len(text) > 1000:
            await message.answer("Your promotion is too long. Please keep it to 1,000 characters or fewer.", reply_markup=submit_menu())
            return
        try:
            submission_id = storage.add_submission(message.from_user.id, message.from_user.username, text)
        except sqlite3.Error:
            logger.exception("Database error while saving submission")
            await message.answer("We couldn't save that submission right now. Please try again.", reply_markup=submit_menu())
            return
        except Exception:
            logger.exception("Unexpected submission error")
            await message.answer("Something went wrong while saving your submission. Please try again.", reply_markup=submit_menu())
            return
        await state.clear()
        await message.answer(
            f"✅ <b>Submission received</b>\n\nReference: <code>SP-{submission_id:06d}</code>\n"
            "Your promotion has been saved for consideration.",
            reply_markup=result_menu("submit"), parse_mode="HTML"
        )
        if settings.admin_id:
            try:
                await message.bot.send_message(settings.admin_id, f"New Starz Promosyon submission SP-{submission_id:06d}\nUser ID: {message.from_user.id}\nText: {text}")
            except TelegramAPIError:
                logger.exception("Failed to notify admin about submission")

    @dp.errors()
    async def global_error(event: ErrorEvent) -> None:
        logger.exception("Unhandled update error", exc_info=event.exception)
        update = event.update
        callback = getattr(update, "callback_query", None)
        message = getattr(update, "message", None)
        if callback is not None:
            try:
                await callback.answer("Something went wrong. Please try again.", show_alert=True)
            except TelegramAPIError:
                logger.exception("Failed to acknowledge callback after an error")
        elif message is not None:
            try:
                await message.answer("Something went wrong. Please use /start to return to the main menu.")
            except TelegramAPIError:
                logger.exception("Failed to send user-facing error message")

    @dp.message()
    async def fallback(message: Message, state: FSMContext) -> None:
        if await state.get_state() == SubmitState.waiting_for_text:
            await message.answer("Please send the promotion as text, or tap Main Menu to cancel.", reply_markup=submit_menu())
            return
        await message.answer("Please use the buttons below or /help to see how the bot works.", reply_markup=main_menu())

    return dp


async def main() -> None:
    settings = Settings.from_env()
    storage = Storage(settings.database_path)
    bot = Bot(token=settings.bot_token)
    dp = build_dispatcher(storage, settings)
    logger.info("Starting Starz Promosyon bot")
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Open the Starz Promosyon menu"),
            BotCommand(command="help", description="Learn how the three functions work"),
        ])
        await bot.set_my_short_description("Promotions, updates and promotion submissions in Telegram.")
        await bot.set_my_description("Starz Promosyon is a Telegram-native promotion hub with three functions: browse promotions, read updates and submit a promotion for consideration.")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Starz Promosyon bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
