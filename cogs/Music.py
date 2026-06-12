import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, url):
        # 1. Verifica se o usuário está num canal de voz
        if not ctx.author.voice:
            return await ctx.send("❌ Precisas de entrar num canal de voz primeiro!")

        channel = ctx.author.voice.channel

        # 2. Conecta ao canal de forma segura e imediata
        vc = ctx.voice_client
        if not vc:
            try:
                vc = await channel.connect()
                print(f"Conectado ao canal de voz: {channel.name}")
            except Exception as e:
                print(f"Erro ao conectar: {e}")
                return await ctx.send("❌ Não consegui conectar ao canal de voz. Verifica as minhas permissões.")

        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True
        }

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        try:
            msg = await ctx.send("⏳ A processar a música no YouTube, aguarde...")

            # 3. Executa o yt-dlp em segundo plano (evita que o bot congele ao entrar)
            loop = asyncio.get_event_loop()
            def get_info():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    return ydl.extract_info(url, download=False)
            
            info = await loop.run_in_executor(None, get_info)
            
            if 'entries' in info:
                info = info['entries'][0]
            
            audio_url = info['url']
            title = info['title']

            # 4. Cria o áudio e toca
            source = await discord.FFmpegOpusAudio.from_probe(audio_url, **ffmpeg_options)

            if vc.is_playing():
                vc.stop()

            vc.play(source)

            embed = discord.Embed(
                title="🎵 Tocando agora",
                description=title,
                color=discord.Color.green()
            )

            await msg.edit(content=None, embed=embed)

        except Exception as e:
            await ctx.send("❌ Ocorreu um erro ao processar o link. Tenta outro vídeo.")
            print(f"Erro detetado na música: {e}")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Música parada e bot desconectado.")

async def setup(bot):
    await bot.add_cog(Music(bot))