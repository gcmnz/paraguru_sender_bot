from dataclasses import dataclass

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from bot.keyboard import (
    set_channel_button,
    back_button,
    get_button,
    accept_keyboard
)
from bot.text import (
    accept_text,
    enter_message_text,
    enter_button_text,
    send_media_text,
    enter_button_url,
    enter_channel_username,
    send_photo_or_video_text,
    get_channel_username_text
)
from token import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dataclass
class Media:
    id_: str
    type_: str


class Form(StatesGroup):
    main = State()
    message_text = State()
    message_media = State()
    button_text = State()
    button_url = State()
    wait_for_accept = State()
    set_channel = State()


@dp.message(Command("set_channel"))
async def process_set_channel(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Form.set_channel)
    await bot.send_message(text=enter_channel_username,
                           chat_id=message.from_user.id,
                           reply_markup=back_button,
                           parse_mode="HTML")


@dp.message()
async def process_message(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        current_state = Form.main

    if not message.text:
        if current_state != Form.message_media:
            return

    data = await state.get_data()
    channel_username: str | None = data.get("channel_username")
    channel_username_text: str = get_channel_username_text(channel_username)

    match current_state:
        case Form.main:
            await state.set_state(Form.message_text)
            await message.answer(text=enter_message_text.format(channel=channel_username_text), parse_mode="HTML", reply_markup=set_channel_button)

        case Form.message_text:
            await state.update_data(message_text=message.text)
            await state.set_state(Form.message_media)
            await message.answer(send_media_text, reply_markup=back_button, parse_mode="HTML")

        case Form.message_media:
            if message.text == "0":
                await state.set_state(Form.button_text)
                await message.answer(enter_button_text, reply_markup=back_button)
                await state.update_data(media=None)

            else:
                # Обработка медиафайлов
                if message.photo:
                    await state.set_state(Form.button_text)
                    photo_id = message.photo[-1].file_id
                    await state.update_data(media=Media(id_=photo_id, type_="photo"))
                    await message.answer(enter_button_text, reply_markup=back_button)
                elif message.video:
                    await state.set_state(Form.button_text)
                    video_id = message.video.file_id
                    await state.update_data(media=Media(id_=video_id, type_="video"))
                    await message.answer(enter_button_text, reply_markup=back_button)
                else:
                    await message.answer(send_photo_or_video_text, reply_markup=back_button)
                    return

        case Form.button_text:
            await state.update_data(button_text=message.text)
            await state.set_state(Form.button_url)
            await message.answer(enter_button_url, reply_markup=back_button)

        case Form.button_url:
            await state.update_data(button_url=message.text)

            data = await state.get_data()

            message_text = data["message_text"]
            button_text = data["button_text"]
            button_url = data["button_url"]
            media = data.get("media")

            keyboard = get_button(button_text, button_url)
            try:
                if media is None:
                    await message.answer(message_text, reply_markup=keyboard, parse_mode="HTML")
                else:
                    if media.type_ == "video":
                        await message.answer_video(
                            video=media.id_,
                            caption=message_text,
                            reply_markup=keyboard,
                            parse_mode="HTML"
                        )
                    elif media.type_ == "photo":
                        await message.answer_photo(
                            photo=media.id_,
                            caption=message_text,
                            reply_markup=keyboard,
                            parse_mode="HTML"
                        )

                    else:
                        await state.set_state(Form.message_text)
                        await bot.send_message(text=enter_message_text.format(channel=channel_username_text),
                                               chat_id=message.from_user.id,
                                               reply_markup=set_channel_button,
                                               parse_mode="HTML")
                        return

                await message.answer(accept_text, reply_markup=accept_keyboard)
                await state.set_state(Form.wait_for_accept)
            except Exception as e:
                await message.answer(text=f"❌ {e}", reply_markup=back_button)

        case Form.set_channel:
            if not message.text.startswith("@"):
                await bot.send_message(text=enter_channel_username,
                                       chat_id=message.from_user.id,
                                       reply_markup=back_button,
                                       parse_mode="HTML")
                return

            await state.update_data(channel_username=message.text)
            await state.set_state(Form.message_text)
            await message.answer(text=enter_message_text.format(channel=f"✅ {message.text}"), parse_mode="HTML", reply_markup=set_channel_button)

        case _:
            await state.set_state(Form.message_text)


@dp.callback_query(lambda c: c.data in ["back", "accept", "reject", "set_channel"])
async def process_keyboard(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    data = await state.get_data()
    channel_username = data.get("channel_username")
    channel_username_text: str = get_channel_username_text(channel_username)

    match callback_query.data:
        case "back":
            match current_state:
                case Form.message_media:
                    await state.set_state(Form.message_text)
                    await bot.edit_message_text(
                        text=enter_message_text.format(channel=channel_username_text),
                        chat_id=callback_query.from_user.id,
                        message_id=callback_query.message.message_id,
                        parse_mode="HTML",
                        reply_markup=set_channel_button
                    )

                case Form.button_text:
                    await state.set_state(Form.message_media)
                    await bot.edit_message_text(
                        text=send_media_text,
                        chat_id=callback_query.from_user.id,
                        message_id=callback_query.message.message_id,
                        parse_mode="HTML",
                        reply_markup=back_button
                    )

                case Form.button_url:
                    await state.set_state(Form.button_text)
                    await bot.edit_message_text(text=enter_button_text,
                                                chat_id=callback_query.from_user.id,
                                                message_id=callback_query.message.message_id,
                                                reply_markup=back_button)

                case Form.wait_for_accept:
                    await state.set_state(Form.message_text)
                    await bot.edit_message_text(text=enter_message_text.format(channel=channel_username_text),
                                                chat_id=callback_query.from_user.id,
                                                message_id=callback_query.message.message_id,
                                                parse_mode="HTML",
                                                reply_markup=set_channel_button)

                case Form.set_channel:
                    await state.set_state(Form.message_text)
                    await bot.edit_message_text(text=enter_message_text.format(channel=channel_username_text),
                                                chat_id=callback_query.from_user.id,
                                                message_id=callback_query.message.message_id,
                                                parse_mode="HTML",
                                                reply_markup=set_channel_button)

                case _:
                    await state.set_state(Form.message_text)

        case "accept":
            if current_state != Form.wait_for_accept:
                await state.set_state(Form.message_text)
                await bot.edit_message_text(
                    text=enter_message_text.format(channel=channel_username_text),
                    chat_id=callback_query.from_user.id,
                    message_id=callback_query.message.message_id,
                    parse_mode="HTML",
                    reply_markup=set_channel_button
                )
                return

            message_text = data["message_text"]
            button_text = data["button_text"]
            button_url = data["button_url"]
            media = data.get("media")

            if channel_username is None:
                await state.clear()
                await state.set_state(Form.set_channel)
                await bot.edit_message_text(text=enter_channel_username,
                                            message_id=callback_query.message.message_id,
                                            chat_id=callback_query.from_user.id,
                                            reply_markup=back_button,
                                            parse_mode="HTML")

                return

            keyboard = get_button(button_text, button_url)
            try:
                if media is None:
                    await bot.send_message(text=message_text, chat_id=channel_username, reply_markup=keyboard, parse_mode="HTML")
                else:
                    if media.type_ == "video":
                        await bot.send_video(
                            video=media.id_,
                            chat_id=channel_username,
                            caption=message_text,
                            reply_markup=keyboard,
                            parse_mode="HTML"
                        )
                    elif media.type_ == "photo":
                        await bot.send_photo(
                            photo=media.id_,
                            chat_id=channel_username,
                            caption=message_text,
                            reply_markup=keyboard,
                            parse_mode="HTML"
                        )

            except Exception as e:
                await state.set_state(Form.message_text)
                await bot.edit_message_text(text=f"❌ {e}",
                                            chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id)

                return

            finally:
                await bot.edit_message_text(text=enter_message_text.format(channel=channel_username_text),
                                            chat_id=callback_query.from_user.id,
                                            message_id=callback_query.message.message_id,
                                            parse_mode="HTML",
                                            reply_markup=set_channel_button)
                await state.clear()
                await state.update_data(channel_username=channel_username)
                await state.set_state(Form.message_text)

        case "reject":
            if current_state != Form.wait_for_accept:
                await state.set_state(Form.message_text)
                await bot.edit_message_text(
                    text=enter_message_text.format(channel=channel_username_text),
                    chat_id=callback_query.from_user.id,
                    message_id=callback_query.message.message_id,
                    parse_mode="HTML",
                    reply_markup=set_channel_button
                )
                return

            await state.clear()
            await state.update_data(channel_username=channel_username)
            await state.set_state(Form.message_text)
            await bot.edit_message_text(text=enter_message_text.format(channel=channel_username_text),
                                        chat_id=callback_query.from_user.id,
                                        message_id=callback_query.message.message_id,
                                        parse_mode="HTML",
                                        reply_markup=set_channel_button)

        case "set_channel":
            await state.set_state(Form.set_channel)
            await bot.edit_message_text(text=enter_channel_username,
                                        message_id=callback_query.message.message_id,
                                        chat_id=callback_query.from_user.id,
                                        reply_markup=back_button,
                                        parse_mode="HTML")
