import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Sem motivo"):
        await member.kick(reason=reason)

        embed = discord.Embed(
            title="👢 Usuário Kickado",
            description=f"{member.mention} foi removido.",
            color=discord.Color.red()
        )

        embed.add_field(name="Motivo", value=reason)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Sem motivo"):
        await member.ban(reason=reason)

        embed = discord.Embed(
            title="🔨 Usuário Banido",
            description=f"{member.mention} foi banido.",
            color=discord.Color.dark_red()
        )

        embed.add_field(name="Motivo", value=reason)

        await ctx.send(embed=embed)

    @commands.command()
    async def limpar(self, ctx, quantidade: int):
        await ctx.channel.purge(limit=quantidade + 1)

        msg = await ctx.send(f"🧹 {quantidade} mensagens apagadas.")
        await msg.delete(delay=3)

async def setup(bot):
    await bot.add_cog(Moderation(bot))