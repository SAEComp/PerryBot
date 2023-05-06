# essential
import os
import discord
import random
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests

load_dotenv()

# Special permissions to be able to use the bot
#intents = discord.Intents.default()
intents = discord.Intents.all()
intents.members = True
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.guilds = True
client = commands.Bot(command_prefix='%', intents=intents)  # bot object


# global random messages variables
lastTwoRandomMessages = [
    "Gosto mais da Ferb do que Phineas", "SAEComp melhor SA"]

# global roles variables
random_emojis = ["🖐", "👌", "🤑", "🍕", "🍣",
                 "🍷", "🥕", "✈", "🎈", "🎃", "🖖", "👋", "🙏"]
escolher_game_roles_id = 824803055345336330
escolher_ano_channel_id = 812769812861157410
fora_da_ec_message_id = 827227120035954758

WELCOME_CHANNEL_ID = 812783690773037107


escolher_ano_emojis = [
    "<:017_ano:938881567823110204>",
    "<:018_ano:938881567823122452>",
    "<:019_ano:938881567927971910>",
    "<:020_ano:938881567781191762>",
    "<:021_ano:938881567579852811>",
    "<:022_ano:938881567969935420>",
    "<:023_ano:1068282529494343730>",
    "<:nenhum_ano:938881567810527282>"
]

anos_roles_id = [
    "812786410184245338",   # 017
    "812767425942650880",   # 018
    "812767411526303794",   # 019
    "812767373521715250",   # 020
    "812767353820676106",   # 021
    "938864548570611712",   # 022
    "1068282004401049692",  # 023
    "827227117866975262"    # Nao eng comper
]

anos_map_from_roles = {
    escolher_ano_emojis[0]: anos_roles_id[0],
    escolher_ano_emojis[1]: anos_roles_id[1],
    escolher_ano_emojis[2]: anos_roles_id[2],
    escolher_ano_emojis[3]: anos_roles_id[3],
    escolher_ano_emojis[4]: anos_roles_id[4],
    escolher_ano_emojis[5]: anos_roles_id[5],
    escolher_ano_emojis[6]: anos_roles_id[6],
    escolher_ano_emojis[7]: anos_roles_id[7]
}


# -------------------------------------------------------------------------------------------
# When the bot logs in
@client.event
async def on_ready():
    print("logged on as ", client.user.name)


@client.event
async def on_member_join(member):

    new_member_private_message = f""" 
Bem vinde ao discord oficial da Engenharia de Computação da USP de São Carlos!

Lembre-se de escolher o seu ano no canal {client.get_channel(escolher_ano_channel_id).mention}
    """

    # Mandar mensagem pro membro falando pra escolher as roles no channel de roles
    try:
        await member.send(new_member_private_message)
        print("Mandei mensagem no privado do membro")
    except:
        print("O novo membro nao deixa mandar mensagem no privado :(")

    # Pegar o channel de novos participantes
    new_member_channel = client.get_channel(WELCOME_CHANNEL_ID)
    new_member_message = member.mention + \
        " seja bem vinde!\t<:perry:824019135880364053> <:p_heart:830601667937435679>"

    await new_member_channel.send(new_member_message)


@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)

    if channel.id == escolher_game_roles_id:  # roles related
        guild = client.get_guild(payload.guild_id)
        all_the_roles = await guild.fetch_roles()
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        embeds = message.embeds
        role_name = embeds[0].title
        for role in all_the_roles:
            if role.name.lower() == role_name.lower():
                role_storage = role

        await member.add_roles(role_storage)
        return

    if channel.id == escolher_ano_channel_id:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        # Pegar a reacao que o usuario colocou
        role_choosed = payload.emoji
        emoji_parsed = f"<:{role_choosed.name}:{role_choosed.id}>"
        # Verificar se foi algum emoji que nao é permitido
        if (emoji_parsed not in escolher_ano_emojis):
            # Remover emoji
            print("uepa entrei aqui")
            await message.clear_reaction(payload.emoji)
            return

        new_role_from_reaction_id = anos_map_from_roles[emoji_parsed]

        # Adicionar a role nas roles do usuario
        role_from_id = guild.get_role(int(new_role_from_reaction_id))

        await member.add_roles(role_from_id)
        return


# -------------------------------------------------------------------------------------------
@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)

    # role related
    if channel.id == escolher_game_roles_id:
        guild = client.get_guild(payload.guild_id)
        all_the_roles = await guild.fetch_roles()
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        embeds = message.embeds
        role_name = embeds[0].title
        for role in all_the_roles:
            if role.name.lower() == role_name.lower():
                role_storage = role

        await member.remove_roles(role_storage)

    if channel.id == escolher_ano_channel_id:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        # Pegar a reacao que o usuario colocou
        role_choosed = payload.emoji
        emoji_parsed = f"<:{role_choosed.name}:{role_choosed.id}>"

        if (emoji_parsed not in escolher_ano_emojis):
            return

        new_role_from_reaction_id = anos_map_from_roles[emoji_parsed]

        # Adicionar a role nas roles do usuario
        role_from_id = guild.get_role(int(new_role_from_reaction_id))

        await member.remove_roles(role_from_id)


# -------------------------------------------------------------------------------------------

@client.command(name="role")
async def RoleManipulation(ctx, *, args):
    guild = ctx.guild

    splitted = args.split(' ')

    if splitted[0] == "add":
        splitted.pop(0)

        if (len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)

        # flag = False
        # for role in ctx.author.roles:
        #     if role.name == "SaeComp": flag = True
        # if(flag == True):

        for role in guild.roles:
            if role_name.lower() == "saecomp":
                response = "Essa role esta indisponível!"
                await ctx.channel.send(response)
                return
            if role_name.lower() == "saecomp_rh":
                response = "Essa role esta indisponível!"
                await ctx.channel.send(response)
                return
            if role_name.lower() == role.name.lower():
                response = "Essa role já existe!"
                await ctx.channel.send(response)
                return

        # Create the role with the name args
        color = random.randint(0, 16777215)
        await guild.create_role(name=role_name, colour=color)

        response_at_channel = "Role criada!"
        await ctx.channel.send(response_at_channel)

        channel = client.get_channel(escolher_game_roles_id)
        embed = discord.Embed(title=str(
            role_name.upper()), description="Reaja a esta mensagem para ganhar a role")
        message = await channel.send(embed=embed)
        await message.add_reaction(random.choice(random_emojis))

    # -------------------------------------------------------------------------------------------

    # remove role if member is from SaeComp
    elif splitted[0] == "remove":
        splitted.pop(0)

        if (len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)

        flag = False
        for role in ctx.author.roles:
            if role.name == "SaeComp" or role.name == "SAEComp_RH":
                flag = True

        if (flag == True):
            for role in guild.roles:
                if role.name.lower() == role_name.lower():
                    channel = client.get_channel(escolher_game_roles_id)
                    async for message in channel.history(limit=1000):
                        embeds = message.embeds
                        for embed in embeds:
                            if embed.title.lower() == role_name.lower():
                                await message.delete()

                    response = "Role removida"
                    await role.delete()
                    await ctx.channel.send(response)
                    return

            response = "Role inexistente"
            await ctx.channel.send(response)

    # -------------------------------------------------------------------------------------------
    # list all the members from a role
    elif splitted[0] == "list":
        splitted.pop(0)
        if (len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)
        flag = False
        for role in guild.roles:
            if role_name.lower() == role.name.lower():
                flag = True
                role_id = role.id

        if (flag == True):
            # get all role memebers
            roleChosen = guild.get_role(role_id)
            role_members = roleChosen.members
            description = str()
            for member in role_members:
                if member.nick == None:
                    description += member.name + '\n'
                else:
                    description += member.nick + '\n'
            title = "Membros de " + str(roleChosen.name)
            embed = discord.Embed(title=title, description=description)
            await ctx.channel.send(embed=embed)
        else:
            response = "Role inexistente"
            await ctx.channel.send(response)

    # role help format
    elif splitted[0] == "help":
        response = "Digite %role add [nome]: para adicionar uma role nova\nDigite %role list [role]: para listar todos os membros desta role"
        await ctx.channel.send(response)

    # -------------------------------------------------------------------------------------------

    else:
        response = "Formato errado\nDigite %role help"
        await ctx.channel.send(response)


@client.event
async def on_message(ctx):

    if ctx.author == client.user:
        return

    # if ctx.content.lower() == 'uepa':
    #     response = "Selecione uma das opções abaixo para definir seu ano de ingresso: \n\n Você pode escolher mais de um ano \n\n Caso o seu ano não esteja presente na lista abaixo mande mensagem para alguem da "

    #     # mencionar saecomp
    #     role_storage = None
    #     for role in ctx.author.roles:
    #         if role.name == "SaeComp":
    #             role_storage = role

    #     response += f"{role_storage.mention} \n\n"

    #     for i, emoji in enumerate(escolher_ano_emojis):
    #         if (i == len(escolher_ano_emojis)-1):
    #             break

    #         response += f"  {emoji}  "

    #     response += "\n\n"

    #     last_emoji = escolher_ano_emojis[-1]

    #     response += f"{last_emoji} Outro curso."

    #     message = await ctx.channel.send(response)
    #     for emoji in escolher_ano_emojis:
    #         await message.add_reaction(emoji)

    # greetings
    if ctx.content.lower() == "oi perry":
        if ctx.author.nick == None:
            response = "Oi " + str(ctx.author.name) + '!'
        else:
            response = "Oi " + str(ctx.author.nick) + '!'
        await ctx.channel.send(response)

    if ctx.content.lower() == "bcc":
         await ctx.channel.send("#XUPABCC!")

    if ctx.content.lower() == "federal":
        await ctx.channel.send("#XUPAFEDERAL!")

    if ctx.content.lower() == "jean":
        await ctx.channel.send("Pau no cu do homer!")

    if ctx.content.lower() == "ku":
        await ctx.channel.send("Me desculpa, membro não encontrado! Provavelmente Umedando")



    await client.process_commands(ctx)

async def Notion_Bot():
    await client.wait_until_ready()
    while True:
        token = 'secret_NALmWtuGhHkehYWvZxSTOE9a4V6lriuVGjPZ0X9YQ7P'

        databaseId = '7300faddb03f45a0b6932149d66510d5'

        headers = {
            "Authorization": "Bearer " + token,
            "Notion-Version": "2022-06-28",
            "content-type": "application/json"
        }
        # Flauta, Cu, Homer e Rio amo vcs <3

        readUrl = f"https://api.notion.com/v1/databases/{databaseId}/query"
        res = requests.request("POST", readUrl, headers=headers)
        dados = res.json()["results"]
        for properties in dados:
            Checkbox = properties["properties"]["Checkbox"]["checkbox"]
            if Checkbox == False:
                nome_do_projeto = properties["properties"]["Name"]["title"][0]["text"]["content"]
                if properties["properties"]["Descrição"]["rich_text"]:
                    descricao = properties["properties"]["Descrição"]["rich_text"][0]["text"]["content"]
                else:
                    descricao = ""
                Solicitante = properties["properties"]["Solicitante"]["created_by"]["name"]
                if properties["properties"]["Data de entrega"]["date"] is None:
                    Entrega = "Não especificado"
                else:
                    Entrega = str(properties["properties"]["Data de entrega"]["date"]["end"])
                if properties["properties"]["Diretoria"]["select"] is None:
                    diretoria = "Não especificado"
                else:
                    diretoria = str(properties["properties"]["Diretoria"]["select"]["name"])
                channel = client.get_channel(845049025018200075)
                await channel.send("Oi @diretoria\n Tem uma nova nota no Notion! Vou te mandar os detalhes:")
                await channel.send("Nome do Projeto: " + nome_do_projeto + "\nDescrição do Projeto: " + descricao + "\nSolicitante: " + Solicitante + "\nDiretoria: " + diretoria + "\nData de Entrega: " + Entrega)
                page_id = properties["id"]
                update_url = f"https://api.notion.com/v1/pages/{page_id}"
                new_props = {
                    "Checkbox": {
                        "checkbox": True
                    }
                }
                update_data = {
                    "properties": new_props
                }
                requests.patch(update_url, headers=headers, json=update_data)


        
        
        await asyncio.sleep(900)
        
SECRET_TOKEN = None
try:
    SECRET_TOKEN = os.environ["TOKEN"]
    if (SECRET_TOKEN == None):
        raise Exception("Erro ao ler o conteudo do .env para o DATABASE_URL")
except:
    raise Exception("Erro ao ler o conteudo do .env para o DATABASE_URL")
@client.event
async def on_ready():
    await Notion_Bot()

client.run(SECRET_TOKEN)
