import discord
from discord.ext import commands

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def anuncio(self, ctx, titulo, *, mensagem):
        embed = discord.Embed(
            title=titulo,
            description=mensagem,
            color=discord.Color.blue()
        )

        embed.set_footer(text=f"Anúncio por {ctx.author}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Embeds(bot))