import os
import disnake
from disnake.ext import commands

bot = commands.Bot(activity=disnake.Game(name="Made in ALEXPress"))


@bot.event
async def on_ready():
    print(f"{bot.user.id} готов к работе!")


for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        bot.load_extension(f"cogs.{file[:-3]}")

bot.run("MTIzMDYzMTMzNjEyNjA1NDQzMA.GOWcLX.B-ExUzRKi5iP_qhINheIiaawSTUJxdYduA3GHE")
