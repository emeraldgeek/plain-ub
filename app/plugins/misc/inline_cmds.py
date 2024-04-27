from app import bot, Message

@bot.add_cmd(cmd="sp")
async def lastfm_status(bot, message: Message):
    try:
        results = await bot.get_inline_bot_results("spotipiebot", "now")
        if results.results:
            first_result = results.results[0]
            await message.reply_inline_bot_result(
                query_id=results.query_id,
                result_id=first_result.id
            )
        else:
            await message.reply("No results found.")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

@bot.add_cmd(cmd="st")
async def lastfm_status(bot, message: Message):
    try:
        results = await bot.get_inline_bot_results("lastfmrobot", "status")
        if results.results:
            first_result = results.results[0]
            await message.reply_inline_bot_result(
                query_id=results.query_id,
                result_id=first_result.id
            )
        else:
            await message.reply("No results found.")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

@bot.add_cmd(cmd="dl")
async def social_dl(bot, message: Message):
    try:
        results = await bot.get_inline_bot_results("rsdl_bot", message.input)
        if results.results:
            first_result = results.results[0]
            await message.reply_inline_bot_result(
                query_id=results.query_id,
                result_id=first_result.id
            )
        else:
            await message.reply("No results found.")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")
