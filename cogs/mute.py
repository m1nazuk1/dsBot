import disnake
from disnake.ext import commands
import datetime
from disnake.ui import View, button


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command(name="mute", description="Замутить пользователя сервера")
    async def timeout(self, interaction, member: disnake.Member, time: str, reason: str):
        timeout_start = datetime.datetime.now()
        timeout_end = timeout_start + datetime.timedelta(minutes=int(time))
        try:
            await member.timeout(reason=reason, until=timeout_end)
        except disnake.HTTPException:
            if not interaction.response.is_done():
                await interaction.response.send_message("Ошибка: сервер Discord не отвечает", ephemeral=True)
            return

        embed = disnake.Embed(title="Пользователь замьючен",
                              description=f"{member.mention} замьючен на {time} минут",
                              color=disnake.Color.red())
        embed.add_field(name="Причина", value=reason)
        embed.add_field(name="Дата и время выдачи мута", value=timeout_start.strftime("`%Y-%m-%d %H:%M:%S`"),
                        inline=False)
        embed.add_field(name="Дата и время окончания мута", value=timeout_end.strftime("`%Y-%m-%d %H:%M:%S`"),
                        inline=False)
        embed.set_footer(text=f"Выдал мут: {interaction.author.display_name}")

        await interaction.response.send_message(f"Мут {member} успешно выдан.", ephemeral=True)

        channel = self.bot.get_channel(1236414560865615995)
        msg = await channel.send(embed=embed)

        view = TimeoutView(member)
        await msg.edit(content="", view=view)

        try:
            interaction_wait = await self.bot.wait_for("message_interaction", check=lambda i: i.message.id == msg.id,
                                                       timeout=int(time) * 1000000000000000000000000000)
            await msg.delete()
        except TimeoutError:
            pass


class TimeoutView(View):
    def __init__(self, member: disnake.Member):
        super().__init__(timeout=None)
        self.member = member

    @button(label="Размутить", style=disnake.ButtonStyle.red, custom_id="unmute")
    async def unmute_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            await self.member.timeout(reason=None, until=None)
            await interaction.response.send_message(f"Мут c {self.member} успешно снят.", ephemeral=True)
        except disnake.HTTPException:
            await interaction.response.send_message("Ошибка: сервер Discord не отвечает", ephemeral=True)
            return


def setup(bot):
    bot.add_cog(Timeout(bot))
