from app import bot, Message
from pyrogram.enums import ParseMode
from g4f.client import Client
from g4f.client.async_client import AsyncClient
from g4f.Provider import MetaAI, Liaobots


@bot.add_cmd(cmd="llm")
async def llama(bot, message: Message):
    client = AsyncClient(
    provider = MetaAI
)

    response = await client.chat.completions.create(
        model="Meta-Llama-3-70b-instruct",
        messages=[{"role": "user", "content": message.input }],
    )

    await message.reply(
                text = f"llama: {response.choices[0].message.content}"
            )

@bot.add_cmd(cmd="gpt")
async def gpt(bot, message: Message):
    client = AsyncClient(
        provider = Liaobots
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": message.input }],
    )

    await message.reply(
                text = f"4o: {response.choices[0].message.content}"
            )

@bot.add_cmd(cmd="cl")
async def claude(bot, message: Message):
    client = AsyncClient(
    provider = Liaobots
)

    response = await client.chat.completions.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": message.input }],
    )

    await message.reply(
                text = f"Claude: {response.choices[0].message.content}"
            )
