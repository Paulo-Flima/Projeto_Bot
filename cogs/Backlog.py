import discord
from discord.ext import commands
from config import LOG_CHANNEL_NAME

class Backlog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, embed):
        channel = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)

        if channel:
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        embed = discord.Embed(
            title="🗑️ Mensagem apagada",
            color=discord.Color.orange()
        )

        embed.add_field(name="Usuário", value=message.author.mention)
        embed.add_field(name="Canal", value=message.channel.mention)
        embed.add_field(name="Conteúdo", value=message.content)

        await self.send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(
            title="📥 Novo membro",
            description=f"{member.mention} entrou no servidor.",
            color=discord.Color.green()
        )

        await self.send_log(member.guild, embed)

async def setup(bot):
    await bot.add_cog(Backlog(bot))