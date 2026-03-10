accept_text: str = "Подтвердите отправку"
enter_message_text: str = """
Введите текст сообщения
Канал: <b>{channel}</b>

Можно использовать HTML-теги:
    &lt;b&gt;<b>жирный</b>&lt;/b&gt;
    &lt;i&gt;<i>курсив</i>&lt;/i&gt;
    &lt;u&gt;<u>подчёркнутый</u>&lt;/u&gt;
    &lt;s&gt;<s>Зачёркнутый</s>&lt;/s&gt;
"""

enter_button_text: str = "Введите текст кнопки:"
send_media_text: str = "Прикрепите фото/видео (не больше одного)\n<b>(0 - пропустить)</b>"
enter_button_url: str = "Введите ссылку для кнопки:"
enter_channel_username: str = "Укажите ссылку на канал <b>(через @)</b>"
send_photo_or_video_text: str = "❌ Отправьте фото или видео (или введите 0, чтобы пропустить)"


def get_channel_username_text(username: str | None) -> str:
    return "❌ Не установлен" if username is None else f"✅ {username}"
