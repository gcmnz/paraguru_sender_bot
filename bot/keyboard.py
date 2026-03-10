from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

back_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back")]
    ]
)

accept_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Отправить", callback_data="accept"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data="reject")]
    ]
)

set_channel_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Установить канал отправки", callback_data="set_channel")]
    ]
)


def get_button(text: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, url=url)]
        ]
    )
