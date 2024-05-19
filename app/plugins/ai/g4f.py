from app import bot, Message
from pyrogram.enums import ParseMode
from g4f.client import Client
from g4f.Provider import MetaAI, Liaobots

@bot.add_cmd(cmd="llm")
async def llama(bot, message: Message):
    client = Client(
    provider = MetaAI
)

    response = client.chat.completions.create(
        model="Meta-Llama-3-70b-instruct",
        messages=[{"role": "user", "content": message.input }],
    )

    await bot.send_message(
                chat_id=message.chat.id,
                text = f"llama: {response.choices[0].message.content}",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=message.reply_id or message.id,
            )

@bot.add_cmd(cmd="gpt")
async def gpt(bot, message: Message):
    client = Client(
        provider = Liaobots
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": message.input }],
    )

    await bot.send_message(
                chat_id=message.chat.id,
                text = f"gpt4: {response.choices[0].message.content}",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=message.reply_id or message.id,
            )

bot.add_cmd(cmd="cl")
async def claude(bot, message: Message):
    client = Client(
    provider = Liaobots
)

    response = client.chat.completions.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": message.input }],
    )

    await bot.send_message(
                chat_id=message.chat.id,
                text = f"Claude: {response.choices[0].message.content}",
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=message.reply_id or message.id,
            )
