import disnake
from disnake.ext import commands
from disnake.ui import View, button
import datetime

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ban", description="Забанить пользователя сервера")
    async def ban(self, interaction, member: disnake.Member, reason: str):
        try:
            await member.ban(reason=reason)
        except disnake.HTTPException:
            if not interaction.response.is_done():
                await interaction.response.send_message("Ошибка: сервер Discord не отвечает", ephemeral=True)
            return

        embed = disnake.Embed(title="Пользователь забанен",
                               description=f"{member.mention} забанен",
                               color=disnake.Color.red())
        embed.add_field(name="Причина", value=reason)
        embed.set_footer(text=f"Забанил: {interaction.author.display_name}")

        await interaction.response.send_message("Пользователь забанен.", ephemeral=True)

        channel = self.bot.get_channel(1236414560865615995)
        msg = await channel.send(embed=embed)

        view = BanView(member)
        await msg.edit(content="", view=view)

class BanView(View):
    def __init__(self, member: disnake.Member):
        super().__init__(timeout=None)
        self.member = member

    @button(label="Разбанить", style=disnake.ButtonStyle.red, custom_id="unban")
    async def unban_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            await self.member.unban()
            await interaction.response.send_message(f"Бан c {self.member} успешно снят.", ephemeral=True)
        except disnake.HTTPException:
            await interaction.response.send_message("Ошибка: сервер Discord не отвечает", ephemeral=True)
            return
        await interaction.message.delete()

def setup(bot):
    bot.add_cog(Ban(bot))