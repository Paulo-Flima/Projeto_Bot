import discord
from discord.ext import commands
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, url):
        if not ctx.author.voice:
            return await ctx.send("Entre em um canal de voz!")

        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            await channel.connect()

        vc = ctx.voice_client

        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info['title']

        source = await discord.FFmpegOpusAudio.from_probe(audio_url)

        vc.play(source)

        embed = discord.Embed(
            title="🎵 Tocando agora",
            description=title,
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Música parada.")

async def setup(bot):
    await bot.add_cog(Music(bot))