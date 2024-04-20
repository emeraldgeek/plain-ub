import json
import mimetypes
import os
import pickle
from io import BytesIO

from pyrogram import filters
from pyrogram.enums import ParseMode

from app import BOT, Convo, Message, bot, Config
from google.ai import generativelanguage as glm
from app.plugins.ai.models import TEXT_MODEL, MEDIA_MODEL, IMAGE_MODEL, basic_check, get_response_text, SAFETY_SETTINGS, GENERATION_CONFIG

PAST = "Implore me to update context with _pas."
HISTORY = "Implore me to update context with _his."
SPECIFIC_GROUP_ID = [-1001898736703, -1002010754513, -1001939171299]
CONTEXT = "Implore me to update context with _fh."

@bot.add_cmd(cmd="fh")
async def fetch_history(bot=bot, message=None):
    history_message_id = int(os.environ.get("HISTORY_MESSAGE_ID"))
    past_message_id = int(os.environ.get("PAST_MESSAGE_ID"))
    history_message, past_message = await bot.get_messages(
        chat_id=Config.LOG_CHAT, message_ids=[history_message_id, past_message_id]
    )
    global HISTORY
    HISTORY = json.loads(history_message.text)
    global PAST
    PAST = json.loads(past_message.text)
    if message is not None:
        await message.reply("Done.")
    if message.chat.id in SPECIFIC_GROUP_ID:
        CONTEXT = PAST
    else:
        CONTEXT = HISTORY

ONEFIVE = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=GENERATION_CONFIG,
    system_instruction=CONTEXT,
    safety_settings=SAFETY_SETTINGS,
)

@bot.add_cmd(cmd="ai")
async def question(bot: BOT, message: Message):
    """
    CMD: AI
    INFO: Ask a question to Gemini AI.
    USAGE: .ai what is the meaning of life.
    """

    if not await basic_check(message):
        return

    prompt = message.input

    response = await ONEFIVE.generate_content_async(prompt)

    response_text = get_response_text(response)

    if not isinstance(message, Message):
        await message.edit(
            text=f"```\n{prompt}```**AI**:\n{response_text.strip()}",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"```\n{prompt}```**AI**:\n{response_text.strip()}",
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=message.reply_id or message.id,
        )


@bot.add_cmd(cmd=["aichat", "rxc"])
async def ai_chat(bot: BOT, message: Message):
    """
    CMD: AICHAT
    INFO: Have a Conversation with Gemini AI.
    USAGE:
        .aichat hello
        keep replying to AI responses
        After 5 mins of Idle bot will export history and stop chat.
        use .load_history to continue
    """
    if not await basic_check(message):
        return
    MODEL= ONEFIVE if message.cmd == "rxc" else TEXT_MODEL
    chat = MODEL.start_chat(history=[])
    try:
        await do_convo(chat=chat, message=message)
    except TimeoutError:
        await export_history(chat, message)


@bot.add_cmd(cmd=["load_history", "lxc"])
async def history_chat(bot: BOT, message: Message):
    """
    CMD: LOAD_HISTORY
    INFO: Load a Conversation with Gemini AI from previous session.
    USAGE:
        .load_history {question} [reply to history document]
    """
    if not await basic_check(message):
        return
    reply = message.replied
    if (
        not reply
        or not reply.document
        or not reply.document.file_name
        or reply.document.file_name != "AI_Chat_History.pkl"
    ):
        await message.reply("Reply to a Valid History file.")
        return
    resp = await message.reply("<i>Loading History...</i>")
    doc: BytesIO = (await reply.download(in_memory=True)).getbuffer()  # NOQA
    history = pickle.loads(doc)
    await resp.edit("<i>History Loaded... Resuming chat</i>")
    MODEL= ONEFIVE if message.cmd == "lxc" else TEXT_MODEL
    chat = MODEL.start_chat(history=history)
    try:
        await do_convo(chat=chat, message=message, history=True)
    except TimeoutError:
        await export_history(chat, message)


async def do_convo(chat, message: Message, history: bool = False):
    prompt = message.input
    reply_to_message_id = message.id
    async with Convo(
        client=message._client,
        chat_id=message.chat.id,
        filters=generate_filter(message),
        timeout=180,
        check_for_duplicates=False,
    ) as convo:
        while True:
            ai_response = await chat.send_message_async(prompt)
            ai_response_text = get_response_text(ai_response)
            text = f"{ai_response_text}"
            _, prompt_message = await convo.send_message(
                text=text,
                reply_to_message_id=reply_to_message_id,
                parse_mode=ParseMode.MARKDOWN,
                get_response=True,
            )
            prompt, reply_to_message_id = prompt_message.text, prompt_message.id


def generate_filter(message: Message):
    async def _filter(_, __, msg: Message):
        if (
            not msg.text
            or not msg.from_user
            or msg.from_user.id != message.from_user.id
            or not msg.reply_to_message
            or not msg.reply_to_message.from_user
            or msg.reply_to_message.from_user.id != message._client.me.id
        ):
            return False
        return True

    return filters.create(_filter)


async def export_history(chat, message: Message):
    doc = BytesIO(pickle.dumps(chat.history))
    doc.name = "AI_Chat_History.pkl"
    caption = get_response_text(
        await chat.send_message_async("Summarize our Conversation into one line.")
    )
    await bot.send_document(chat_id=message.from_user.id, document=doc, caption=caption)

@bot.add_cmd(cmd=["r","rx"])
async def reya(bot: BOT, message: Message):
    """
    CMD: R
    INFO: Ask a question to Reya.
    USAGE: .r How to be strong?
    """
    if not (await basic_check(message)):  # fmt:skip
        return
    MODEL = MEDIA_MODEL if message.cmd == "r" else ONEFIVE
    name = "Leaf"
    replied = message.replied

    if replied:
        reply_input = f"{replied.from_user.first_name}: {replied.text}"

        if not message.input:
            prompt = f"{reply_input}"
        else:
            prompt = f"{reply_input}\n{name}: {message.input}"

    else:
        prompt = f"{name}: {message.input}"

    if replied and replied.photo:
        file = await replied.download(in_memory=True)

        mime_type, _ = mimetypes.guess_type(file.name)
        if mime_type is None:
            mime_type = "image/unknown"

        image_blob = glm.Blob(mime_type=mime_type, data=file.getvalue())
        prompt = (
            REYA_INSTRUCTIONS
            + f"Now, about the image : {message.input}"
        )

        if message.cmd == "rx":
            convo = ONEFIVE.start_chat(history=[])
            response = convo.send_message([message.input, image_blob])
            
        else:
            response = await IMAGE_MODEL.generate_content_async([prompt, image_blob])

    elif replied and (replied.audio or replied.voice):
        file = await replied.download()
        audio_file = genai.upload_file(path = file, display_name="Voice Note")
    

        response = await ONEFIVE.generate_content_async([ message.input, audio_file])
        response_text = response.text
        await bot.send_message(
            chat_id=message.chat.id,
            text=response_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=message.id,
        )

    else:
        convo = MODEL.start_chat(history=[])
        response = convo.send_message(prompt)

    response_text = get_response_text(response)
    await bot.send_message(
        chat_id=message.chat.id,
        text = response_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=message.reply_id or message.id,
    )
