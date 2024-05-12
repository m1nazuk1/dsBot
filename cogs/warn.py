import os

import certifi

os.environ['SSL_CERT_FILE'] = certifi.where()
import disnake
from disnake.ext import commands
from disnake.ui import View, button
import datetime


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns = {}

    @commands.slash_command(name="warn", description="Выдать предупреждение пользователю")
    async def warn(self, interaction, member: disnake.Member, reason: str):
        try:
            await member.send(f"Вы получили предупреждение на сервере за: {reason}")
            await interaction.response.send_message(f"{member} получил предупреждение за {reason}", ephemeral=True)
        except disnake.HTTPException:
            if not interaction.response.is_done():
                await interaction.response.send_message("Ошибка: сервер Discord не отвечает", ephemeral=True)
            return

        if member.id not in self.warns:
            self.warns[member.id] = []

        self.warns[member.id].append({"reason": reason, "timestamp": datetime.datetime.now()})

        if len(self.warns[member.id]) >= 6:
            await self.ban_user(member)

    async def ban_user(self, member: disnake.Member):
        ban_end = datetime.datetime.now() + datetime.timedelta(days=365)
        await member.ban(reason=f"Достигнуто максимальное количество предупреждений", delete_message_days=0)

        embed = disnake.Embed(
            title="Пользователь был забанен",
            description=f"{member.mention} был забанен за количество предупреждений",
            color=disnake.Color.red()
        )
        embed.set_footer(text=f"Забанил: пидарас")

        channel = self.bot.get_channel(1236414560865615995)
        msg = await channel.send(embed=embed)

        view = UnbanView(member)
        await msg.edit(view=view)

    @commands.slash_command(name="warns", description="Посмотреть все предупреждения пользователя")
    async def warns(self, interaction, member: disnake.Member):
        if member.id not in self.warns or not self.warns[member.id]:
            await interaction.response.send_message("У пользователя нет предупреждений.", ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"Предупреждения пользователя {member.display_name}",
            color=disnake.Color.orange()
        )

        for idx, warn in enumerate(self.warns[member.id], start=1):
            embed.add_field(name=f"Предупреждение {idx}",
                            value=f"**Причина:** {warn['reason']}\n**Дата и время:** {warn['timestamp']}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
class UnbanView(View):
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
class WarnView(View):
    def __init__(self, member: disnake.Member):
        super().__init__(timeout=None)
        self.member = member

    @button(label="Закрыть", style=disnake.ButtonStyle.red, custom_id="close_warns")
    async def close_warns_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.message.delete()


def setup(bot):
    bot.add_cog(Warn(bot))
