import google.generativeai as genai
import os
import json
from app import Message, extra_config, Config, bot


async def init_task():
    if extra_config.GEMINI_API_KEY:
        genai.configure(api_key=extra_config.GEMINI_API_KEY)


GENERATION_CONFIG = {"temperature": 0.75, "max_output_tokens": 3096}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

PAST = []
HISTORY = []
SPECIFIC_GROUP_ID = [-1001898736703, -1002010754513]
CONTEXT = "Implore me to update context.'

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

TEXT_MODEL = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=GENERATION_CONFIG,
    safety_settings=SAFETY_SETTINGS,
)

IMAGE_MODEL = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=GENERATION_CONFIG,
    safety_settings=SAFETY_SETTINGS,
)

MEDIA_MODEL = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=GENERATION_CONFIG,
    safety_settings=SAFETY_SETTINGS,
)

ONEFIVE = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=GENERATION_CONFIG,
    system_instruction=CONTEXT,
    safety_settings=SAFETY_SETTINGS,
)

async def basic_check(message: Message):
    if not extra_config.GEMINI_API_KEY:
        await message.reply(
            "Gemini API KEY not found."
            "\nGet it <a href='https://makersuite.google.com/app/apikey'>HERE</a> "
            "and set GEMINI_API_KEY var."
        )
        return
    if not message.input and not message.replied:
        await message.reply("Ask a Question.")
        return
    return 1


def get_response_text(response):
    return "\n".join([part.text for part in response.parts])
