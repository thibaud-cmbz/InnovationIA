import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import openai
import asyncio

load_dotenv()
intents = discord.Intents.all()
token = os.environ.get("MY_TOKEN")
openai_key = os.environ.get("OPENAPI_KEY")
openai.api_key = openai_key

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_reaction_add(reaction, user):
    channel_name = "aventure"
    channel = discord.utils.get(reaction.message.guild.channels, name=channel_name)
    if user == bot.user:
        return
    if reaction.emoji == '✅' and reaction.message.author == bot.user and discord.utils.get(user.roles, name='aventure') is None :
        role = discord.utils.get(reaction.message.guild.roles, name='aventure')
        if role:
            await user.add_roles(role)
            if channel:
                await channel.send(f"{user.mention}, Bienvenue dans l'aventure")
            else:
                print(f"Channel '{channel_name}' non trouvé.")
        else:
            print("Rôle 'aventure' introuvable.")

@bot.command(name='ping')
async def ping(ctx):
    try:
        completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un chatbot, réponds à la commande ping"},
                        {"role": "user", "content": "ping"},
                    ]
                )
        await ctx.send(f"{completion.choices[0].message.content.strip()})")
    except Exception as e:
        await ctx.send(f"Erreur lors de la requête à OpenAI : {e}")

@bot.event
async def on_message(message):
    # Ne faites rien si le bot est l'auteur du message
    if message.author == bot.user:
        return
    # Si le message contient "remove"
    if "remove" in message.content.lower():
        role = discord.utils.get(message.guild.roles, name='aventure')
        # Si le rôle existe et que l'utilisateur l'a
        if role and role in message.author.roles:
            await message.author.remove_roles(role)
    # N'oubliez pas de traiter les autres commandes également
    await bot.process_commands(message)


@bot.command(name='presentation')
async def presentation(ctx):
    await ctx.send("Bonjour, je suis un bot discord créé pour le serveur discord de Neopolis.")

def create_embed(title : str, description : str, img_url : str, color: str, fields: list):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    for i in range (0, len(fields), 2):
        embed.add_field(name=fields[i + 1], value=fields[i], inline=False)
    embed.set_image(url=img_url)
    return embed

async def send_with_embed(ctx, image_path):
    with open(image_path, 'rb') as f:
        picture = discord.File(f, filename="image.png")  # Vous pouvez changer le nom de fichier si nécessaire
        # embed = create_embed("Votre Titre", "Votre Description", "attachment://image.png", 0x00ff00, [])
        embed = create_embed("Partez a l'assaut de la NéoZone 51",
                "Réagissez a l'émoji pour commencer le jeu.",
                "attachment://image.png",
                0x00ff00,
                ["✅", "Réagissez avec si vous voulez participer", "❌", "Réagissez avec si vous ne voulez pas participer"])
    message = await ctx.send(file=picture, embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")

@bot.command(name='start')
async def game(ctx):
    await send_with_embed(ctx, "Assets/banner.png")

async def send_if_2000(ctx, message):
    if len(message) > 2000:
        while len(message) > 2000:
            await ctx.send(message[:2000])
            message = message[2000:]
    else:
        await ctx.send(message)

@bot.command(name='scenario')
async def scenario(ctx):
    etapes = ["Arrivé aux abords de la base", "Persuader le militaire", "Escalader le grillage", "Echapper aux serpents mutants", "Ouvrir la dernière porte"]
    response = ""
    async with ctx.typing():
        try:
            for i in range(5):
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un aventurier qui nous suis dans notre aventure pour entrer dans la Zone 51, on doit faire face à des obstacles et les surmonter pour avancer dans l'aventure, on est à l'étape : " + etapes[i] + "explique la situation et présente-la-moi afin que je te dise comment on peut s'en sortir. Tu es libre d'inventer des noms mais ne pars pas trop loin et reste dans la réalité. Soit Role play, soit logique dans ce que tu dis et amuse-toi bien !"},
                        {"role": "user", "content": "explique la situation actuelle"},
                    ]
                )
                print("request done")
                response = completion.choices[0].message.content.strip()
                await send_if_2000(ctx, response)

                # Attendre 1 minutes avant de continuer
                await asyncio.sleep(60)
                print("take message")

                channel = bot.get_channel(int("1166346246655590533"))

                max_thumbs_up_count = -1  # pour suivre le nombre maximum de réactions de pouce levé
                most_liked_message = None  # pour suivre le message avec le plus de réactions de pouce levé

                async for message in channel.history(limit=50):  # ajustez le nombre si nécessaire
                    if message.author == bot.user:
                        break
                    for reaction in message.reactions:
                        if reaction.emoji == '👍' and reaction.count > max_thumbs_up_count:
                            max_thumbs_up_count = reaction.count
                            most_liked_message = message

                if most_liked_message:
                    print(f"Dernier message avec le plus de pouces levés: {most_liked_message.content}")
                    await ctx.send(f"Message choisi : {most_liked_message.content}")
                else:
                    print("no message detected")
                    await ctx.send("Aucun message n'a été détecté")

        except Exception as e:
            await ctx.send(f"Erreur lors de la requête à OpenAI : {e}")



bot.run(token)
