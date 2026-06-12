import discord
from discord.ext import commands
import random
import json
import os
import aiohttp  # Nova biblioteca para comunicar com a PokéAPI

# Ficheiro onde os inventários serão guardados
DATA_FILE = "pokemons.json"

class TradeView(discord.ui.View):
    def __init__(self, cog, author, target, meu_pokemon, pokemon_dele):
        super().__init__(timeout=120)
        self.cog = cog
        self.author = author
        self.target = target
        self.meu_pokemon = meu_pokemon
        self.pokemon_dele = pokemon_dele

    @discord.ui.button(label="Aceitar Troca", style=discord.ButtonStyle.success, emoji="✅")
    async def btn_aceitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Esta troca não é para ti!", ephemeral=True)

        sucesso, msg = self.cog.executar_troca(str(self.author.id), str(self.target.id), self.meu_pokemon, self.pokemon_dele)
        
        if sucesso:
            await interaction.response.send_message(f"🎉 **Troca concluída com sucesso!**\n{self.author.mention} recebeu `{self.pokemon_dele}` e {self.target.mention} recebeu `{self.meu_pokemon}`!")
        else:
            await interaction.response.send_message(f"❌ A troca falhou: {msg}")
        
        self.stop()

    @discord.ui.button(label="Recusar", style=discord.ButtonStyle.danger, emoji="❌")
    async def btn_recusar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target.id:
            return await interaction.response.send_message("Esta troca não é para ti!", ephemeral=True)
            
        await interaction.response.send_message("🛑 A troca foi recusada.")
        self.stop()


class Pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = self.carregar_dados()

    # --- FUNÇÕES DE DADOS ---
    def carregar_dados(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def salvar_dados(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.db, f, indent=4)

    def formatar_nome(self, pokemon_dict):
        if pokemon_dict.get("shiny"):
            return f"✨ Shiny {pokemon_dict['name']}"
        return pokemon_dict["name"]

    # --- EVENTO: MENSAGENS E SORTEIOS ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Chance de 1 em 15 de aparecer um Pokémon
        chance_aparecer = random.randint(1, 2)
        
        if chance_aparecer == 1:
            # Sorteia um ID de Pokémon (atualmente a PokéAPI vai até ao 1025)
            pokemon_id = random.randint(1, 1025)
            pokemon_nome = "Desconhecido"

            # Comunica com a PokéAPI para buscar o nome do Pokémon
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}") as response:
                        if response.status == 200:
                            data = await response.json()
                            # A API devolve tudo em minúsculas, capitalize() mete a primeira letra maiúscula
                            pokemon_nome = data['name'].capitalize() 
                        else:
                            # Easter Egg se a API falhar
                            pokemon_nome = "MissingNo" 
            except Exception as e:
                print(f"Erro ao buscar Pokémon na API: {e}")
                return # Aborta silenciosamente se falhar a internet
            
            # Sorteio do Shiny (exatamente como pediste: 0 ou 67)
            sorteio_shiny = random.randint(0, 100)
            is_shiny = sorteio_shiny in [0, 67]

            novo_pokemon = {
                "name": pokemon_nome,
                "shiny": is_shiny
            }

            user_id = str(message.author.id)
            if user_id not in self.db:
                self.db[user_id] = []
            
            self.db[user_id].append(novo_pokemon)
            self.salvar_dados()

            nome_display = self.formatar_nome(novo_pokemon)
            await message.channel.send(f"🎉 Opa! {message.author.mention} encontrou um **{nome_display}** selvagem enquanto conversava!")

    # --- COMANDOS ---
    @commands.command(aliases=["pokemons", "inv"])
    async def inventario(self, ctx):
        user_id = str(ctx.author.id)
        inventario = self.db.get(user_id, [])

        if not inventario:
            return await ctx.send("Tu ainda não tens nenhum Pokémon. Continua a mandar mensagens para encontrar um!")

        lista_formatada = [self.formatar_nome(p) for p in inventario]
        embed = discord.Embed(title=f"🎒 Inventário de {ctx.author.display_name}", color=discord.Color.blue())
        
        texto_inventario = "\n".join(f"• {nome}" for nome in lista_formatada)
        if len(texto_inventario) > 4000:
            texto_inventario = texto_inventario[:4000] + "\n... e muitos mais!"
            
        embed.description = texto_inventario
        await ctx.send(embed=embed)

    @commands.command()
    async def soltar(self, ctx, *, nome_pokemon: str):
        user_id = str(ctx.author.id)
        inventario = self.db.get(user_id, [])

        for p in inventario:
            nome_completo = self.formatar_nome(p).lower()
            if nome_pokemon.lower() == nome_completo or nome_pokemon.lower() == p["name"].lower():
                inventario.remove(p)
                self.salvar_dados()
                return await ctx.send(f"👋 Libertaste o teu **{self.formatar_nome(p)}**. Ele voltou para a natureza!")
                
        await ctx.send("❌ Não tens esse Pokémon. Escreve o nome exato (ex: `!soltar Shiny Pikachu`).")

    @commands.command()
    async def dar(self, ctx, membro: discord.Member, *, nome_pokemon: str):
        if membro == ctx.author:
            return await ctx.send("Não podes dar um Pokémon a ti mesmo!")
        if membro.bot:
            return await ctx.send("Bots não podem ter Pokémon!")

        user_id = str(ctx.author.id)
        target_id = str(membro.id)
        inventario_autor = self.db.get(user_id, [])

        pokemon_encontrado = None
        for p in inventario_autor:
            if nome_pokemon.lower() in [self.formatar_nome(p).lower(), p["name"].lower()]:
                pokemon_encontrado = p
                break

        if not pokemon_encontrado:
            return await ctx.send("❌ Não tens esse Pokémon para dar!")

        inventario_autor.remove(pokemon_encontrado)
        
        if target_id not in self.db:
            self.db[target_id] = []
        self.db[target_id].append(pokemon_encontrado)
        
        self.salvar_dados()
        await ctx.send(f"🎁 {ctx.author.mention} deu um **{self.formatar_nome(pokemon_encontrado)}** de presente para {membro.mention}!")

    @commands.command()
    async def trocar(self, ctx, membro: discord.Member, meu_pokemon: str, pokemon_dele: str):
        if membro == ctx.author or membro.bot:
            return await ctx.send("❌ Menção inválida para troca.")

        user_id = str(ctx.author.id)
        target_id = str(membro.id)

        if not self.tem_pokemon(user_id, meu_pokemon):
            return await ctx.send(f"❌ Tu não tens o Pokémon `{meu_pokemon}`!")
        if not self.tem_pokemon(target_id, pokemon_dele):
            return await ctx.send(f"❌ O {membro.mention} não tem o Pokémon `{pokemon_dele}`!")

        view = TradeView(self, ctx.author, membro, meu_pokemon, pokemon_dele)
        await ctx.send(f"🔄 **PROPOSTA DE TROCA** 🔄\n{membro.mention}, o {ctx.author.mention} quer trocar o **{meu_pokemon}** dele pelo teu **{pokemon_dele}**!\n\nAceitas?", view=view)

    # --- FUNÇÕES DE APOIO ---
    def tem_pokemon(self, user_id, nome_pokemon):
        inventario = self.db.get(user_id, [])
        for p in inventario:
            if nome_pokemon.lower() in [self.formatar_nome(p).lower(), p["name"].lower()]:
                return True
        return False

    def executar_troca(self, id_autor, id_alvo, nome_autor, nome_alvo):
        if not self.tem_pokemon(id_autor, nome_autor) or not self.tem_pokemon(id_alvo, nome_alvo):
            return False, "Alguém já não possui o Pokémon combinado."

        poke_autor = None
        for p in self.db[id_autor]:
            if nome_autor.lower() in [self.formatar_nome(p).lower(), p["name"].lower()]:
                poke_autor = p
                self.db[id_autor].remove(p)
                break

        poke_alvo = None
        for p in self.db[id_alvo]:
            if nome_alvo.lower() in [self.formatar_nome(p).lower(), p["name"].lower()]:
                poke_alvo = p
                self.db[id_alvo].remove(p)
                break

        self.db[id_autor].append(poke_alvo)
        self.db[id_alvo].append(poke_autor)
        self.salvar_dados()

        return True, ""


async def setup(bot):
    await bot.add_cog(Pokemon(bot))