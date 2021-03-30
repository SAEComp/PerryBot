# essential
import os, time, json, nacl, discord, random, requests, datetime
from discord.ext import commands, tasks

from application import app, parseResponse, writeInfo, removeInfo, doesUserExits, getInfoFromUser, getInfoFromAllUsers #user handling
from database_handler import add_random_text, get_random_text, remove_random_text, get_all_text #database related
from listafuvest import runScrapCheck, secretpdf #search of fuvest's list
from snake import SnakeGame, VerifyMatriz, GetCurrentTime, GetLastSnakeMessageId, StringOfMatriz #snake game

#Special permissions to be able to use the bot
intents = discord.Intents.default()
intents.members = True
intents.emojis = True
intents.messages = True
intents.reactions = True
intents.guilds = True
client = commands.Bot(command_prefix = '%', intents=intents) #bot object


#global random messages variables
lastTwoRandomMessages = ["Gosto mais da Ferb do que Phineas", "SAEComp melhor SA"]

#global roles variables
random_emojis = ["🖐" , "👌" , "🤑" , "🍕" , "🍣" , "🍷" , "🥕" , "✈" , "🎈" , "🎃" , "🖖" , "👋" , "🙏"]
escolher_roles_id = 824803055345336330

#global snakeGame variables
SnakeDict = {
    "lastSnakeMessageId": None,
    "reactionsCounter": [0,0,0,0] ,
    "snake_emojis": ["⬆" , "⬇" , "➡", "⬅"],
    "snakeChannelId": 825497428693745744 #jogo-da-cobrinha channel id
}
wait_time = 2 #minutes


#-------------------------------------------------------------------------------------------
# When the bot logs in
@client.event
async def on_ready():
    print("logged on as ", client.user.name)

    # Check here the snake game last save in the database ###todo###
    

#-------------------------------------------------------------------------------------------

# Seaches the latest fuvest's list of aproved students
@tasks.loop(minutes=30)
async def SearchForTheList():
    flag, filename = runScrapCheck()
    if(flag == False):
        flag, filename = secretpdf(list_number=2)
    if(flag == True):
        channel = client.get_channel(823653472204226561)
        response = "Saiu a lista de chamada"
        await channel.send(response)
        await channel.send(file=discord.File(filename))
        await channel.send(file=discord.File("names.txt"))
    else:
        channel = client.get_channel(823721250647441421)
        await channel.send("Acabei de olhar. Ainda não saiu")

#-------------------------------------------------------------------------------------------

@tasks.loop(minutes=wait_time)
async def VerifySnakeGame(game):
    #ver se teve reacao na mensagem
    #ver a reacao que foi mais votada
    #mandar uma nova mensagem com a matriz atualizada, e os emojis de novo

    #verify if the message had any added reactions
    flag = False
    for reaction in SnakeDict["reactionsCounter"]:
        if reaction != 0:
            flag = True

    channel = client.get_channel(SnakeDict["snakeChannelId"])
    if flag:

        #get the best move
        best_move = SnakeDict["reactionsCounter"].index(max(SnakeDict["reactionsCounter"]))

        move = None
        if(best_move == 0):
            move = 'w'
        elif(best_move == 1):
            move = 's'
        elif(best_move == 2):
            move = 'd'
        elif(best_move == 3):
            move = 'a'

        game_state = game.update(move) #Make the move

        if(game_state == False): #check the game state
            VerifySnakeGame.stop()
            lose_response = "Jogo acabou!\nScore: " + str(game.Length_of_snake - 1)
            await channel.send(lose_response)
            return
    
        #clear the reaction counter
        SnakeDict["reactionsCounter"] = [0 for _ in range(len(SnakeDict["reactionsCounter"]))]
        
        #get the new matrix and send it
        response_matriz = await StringOfMatriz(game)

        message = await channel.send(response_matriz)
        SnakeDict["lastSnakeMessageId"] = message.id
        for emoji in SnakeDict["snake_emojis"]:
            await message.add_reaction(emoji)

    else:
        try:
            message = await channel.fetch_message(SnakeDict["lastSnakeMessageId"])
            response_matriz = await StringOfMatriz(game)
            await message.edit(content=response_matriz)
        except:
            pass

#-------------------------------------------------------------------------------------------

@client.command(name="startgame")
async def HandleSnakeGame(ctx, *args):
    if VerifySnakeGame.is_running() == False:
        game = SnakeGame()

        response_matriz = await StringOfMatriz(game)
        
        message = await ctx.channel.send(response_matriz)
        SnakeDict["lastSnakeMessageId"] = message.id
        for emoji in SnakeDict["snake_emojis"]:
            await message.add_reaction(emoji)

        VerifySnakeGame.start(game) #comeca a função VerifySnakeGame
    else:
        response = "Jogo já em andamento!"
        await ctx.channel.send(response)

#-------------------------------------------------------------------------------------------
@client.command(name="stopgame")
async def HandleStopSnakeGame(ctx,*args):
    VerifySnakeGame.stop()
    response = "Jogo terminado!\n"
    await ctx.channel.send(response)
#-------------------------------------------------------------------------------------------

@client.event
async def on_raw_reaction_add(payload):
    channel = client.get_channel(payload.channel_id)
    
    if channel.id == escolher_roles_id: #roles related
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

    #snake game related
    if payload.message_id == SnakeDict["lastSnakeMessageId"] and payload.user_id != client.user.id:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        if not str(payload.emoji) in SnakeDict["snake_emojis"]: #if the emoji isnt one of the four emojis, remove it
            print(payload.emoji)
            await message.clear_reaction(payload.emoji)
            return

        #if the user has added more than one reaction
        usuario = payload.user_id
        counter = 0
        message_reactions = message.reactions
        for reaction in message_reactions:
            async for user in reaction.users():
                if usuario == user.id and user.id != client.user.id:
                    counter += 1
                if(counter >= 2):
                    await reaction.remove(user)
                    return      

        #add the reaction to the list of reactions
        emoji = str(payload.emoji)
        if emoji == SnakeDict["snake_emojis"][0]: #up arrow
            SnakeDict["reactionsCounter"][0] += 1
        elif emoji == SnakeDict["snake_emojis"][1]: #down arow
            SnakeDict["reactionsCounter"][1] += 1
        elif emoji == SnakeDict["snake_emojis"][2]: #rigth arrow
            SnakeDict["reactionsCounter"][2] += 1
        elif emoji == SnakeDict["snake_emojis"][3]: #left arrow
            SnakeDict["reactionsCounter"][3] += 1

#-------------------------------------------------------------------------------------------
@client.event
async def on_raw_reaction_remove(payload):
    channel = client.get_channel(payload.channel_id)
    
    #role related
    if channel.id == escolher_roles_id:
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

    #snake game related
    if payload.message_id == SnakeDict["lastSnakeMessageId"] and payload.user_id != client.user.id:
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        
        emoji = str(payload.emoji)
        if emoji == SnakeDict["snake_emojis"][0] and SnakeDict["reactionsCounter"][0] != 0: #up arrow
            SnakeDict["reactionsCounter"][0] -= 1
        elif emoji == SnakeDict["snake_emojis"][1] and SnakeDict["reactionsCounter"][1] != 0: #down arow
            SnakeDict["reactionsCounter"][1] -= 1
        elif emoji == SnakeDict["snake_emojis"][2] and SnakeDict["reactionsCounter"][2] != 0: #rigth arrow
            SnakeDict["reactionsCounter"][2] -= 1
        elif emoji == SnakeDict["snake_emojis"][3] and SnakeDict["reactionsCounter"][3] != 0: #left arrow
            SnakeDict["reactionsCounter"][3] -= 1
        
            
#-------------------------------------------------------------------------------------------

@client.command(name="role")    
async def RoleManipulation(ctx, *, args):
    guild = ctx.guild
    
    splitted = args.split(' ')

    if splitted[0] == "add":
        splitted.pop(0)

        if(len(splitted) == 0):
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
            if role_name.lower() == role.name.lower():
                response = "Essa role já existe!"
                await ctx.channel.send(response)
                return

        #Create the role with the name args
        color = random.randint(0,16777215)
        await guild.create_role(name=role_name, colour=color)

        response_at_channel = "Role criada!"
        await ctx.channel.send(response_at_channel)

        channel = client.get_channel(escolher_roles_id)
        embed = discord.Embed(title=str(role_name.upper()), description="Reaja a esta mensagem para ganhar a role")
        message = await channel.send(embed=embed)
        await message.add_reaction(random.choice(random_emojis))


    #-------------------------------------------------------------------------------------------

    #remove role if member is from SaeComp
    elif splitted[0] == "remove":
        splitted.pop(0)

        if(len(splitted) == 0):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return

        role_name = ' '.join(splitted)

        flag = False
        for role in ctx.author.roles: 
            if role.name == "SaeComp": flag = True

        if(flag == True):
            for role in guild.roles:
                if role.name.lower() == role_name.lower():
                    channel = client.get_channel(escolher_roles_id)
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

    #-------------------------------------------------------------------------------------------
    #list all the members from a role
    elif splitted[0] == "list":
        splitted.pop(0)
        if(len(splitted) == 0 ):
            response = "Formato errado\nDigite %role help"
            await ctx.channel.send(response)
            return
        
        role_name = ' '.join(splitted)
        flag = False
        for role in guild.roles:
            if role_name.lower() == role.name.lower():
                flag = True
                role_id = role.id
        
        if(flag == True):
            #get all role memebers
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
        
    #role help format
    elif splitted[0] == "help":
        response = "Digite %role add [nome]: para adicionar uma role nova\nDigite %role list [role]: para listar todos os membros desta role"
        await ctx.channel.send(response)

    #-------------------------------------------------------------------------------------------

    else:
        response = "Formato errado\nDigite %role help"
        await ctx.channel.send(response)

    
#-------------------------------------------------------------------------------------------

#random messages handling
@client.command(name="random")
async def HandleRandomEvents(ctx, *args):

    largs = list(args)
  
    if(len(largs) == 0):
        #send here the random message

        flag = False
        while flag == False:
            try:
                ret = get_random_text()
            except:
                pass

            if ret != lastTwoRandomMessages[0]: 
                flag = True
                lastTwoRandomMessages[1] = lastTwoRandomMessages[0]
                lastTwoRandomMessages[0] = ret
                break
        
        await ctx.channel.send(ret)
        

    elif(largs[0] == "add"):
        #add the message into the database
        largs.pop(0)
        if(len(largs) == 0):
            await ctx.channel.send("Formato errado digite %random help")
            return
        
        #add data
        new_message = ' '.join(largs)
        
        try:
            add_random_text(new_message)
        except:
            await ctx.channel.send("Essa mensagem já existe")
            return

        response = new_message + " adicionado!"
        await ctx.channel.send(response)


    elif(largs[0] == "remove"):
        largs.pop(0)
        if(len(largs) == 0):
            await ctx.channel.send("Formato errado digite %random help")
            return
        
        message_to_remove = ' '.join(largs)

        try:
            remove_random_text(message_to_remove)
        except:
            await ctx.channel.send("Mensagem inexistente")
            return

        await ctx.channel.send("Mensagem removida")


    elif(largs[0] == "help"):
        response = "    ->%random: para uma mensagem aleatoria\n->%random add [mensagem]: adiciona a mensagem digitada\n->%random remove [mensagem]: remove a mensagem digitada"
        await ctx.channel.send(response)

    #list all the messages ###MUST BE USED WITH CAUTION###
    elif(largs[0] == "list"):
        flag = False
        for role in ctx.author.roles: 
            if role.name == "SaeComp": flag = True
        if(flag == True):
            all_text = get_all_text()
            for text in all_text:
                await ctx.channel.send(text[0])
    else:
        response = "Formato errado\n    ->%random: para uma mensagem aleatoria\n    ->%random add [mensagem]: adiciona a mensagem digitada\n    ->%random remove [mensagem]: remove a mensagem digitada"
        await ctx.channel.send(response)


@client.event
async def on_message(ctx):
    
    if ctx.author == client.user:
        return

    #greetings
    if ctx.content.lower() == "oi perry":
        if ctx.author.nick == None:
                response = "Oi " + str(ctx.author.name) + '!'
        else:
            response = "Oi " + str(ctx.author.nick) + '!'
        await ctx.channel.send(response)

    #handle usernames from different platforms and stores them
    if ctx.content.startswith("*") and ctx.content.lower() != "*remover" and ctx.channel.name == "🔭user-de-jogo" and ":" in ctx.content:
        get_message = ctx.content
        flag, content = app(get_message, ctx.author)
        if(flag == 0):
            await ctx.channel.send(content)
        else:
            response = parseResponse(content, ctx.author)
            await ctx.channel.send(response)
            writeInfo(content, ctx.author)

    #remove a requested username from a discord member
    if ctx.content.lower() == "*remover" and ctx.channel.name == "🔭user-de-jogo":
        removeInfo(ctx.author)
        response = "Dados Removidos " + ctx.author.mention
        await ctx.channel.send(response)

    #get information from a certain member.
    if ctx.content.startswith('%') and ctx.content.lower() != "%getall" and ctx.content.lower() != "%saiu?":
        user = ctx.content.replace('%' , '')
        flag, user = doesUserExits(user)
        if (flag == True):
            response = getInfoFromUser(user)
            await ctx.channel.send(response)


    #get info from all users
    if ctx.content.lower() == "%getall" and ctx.channel.name == "info-users":
        flag = False
        for role in ctx.author.roles:
            if role.name =="SaeComp":
                flag = True
            
        if(flag == True):
            getInfoFromAllUsers()
            await ctx.channel.send(file=discord.File("users/getAllInfo.txt"))

    if ctx.content.lower() == "bcc":
        await ctx.channel.send("#XUPABCC")

    if ctx.content.lower() == "federal":
        await ctx.channel.send("#XUPAFEDERAL")

    if ctx.content.lower() == "%get debugg json" and ctx.channel.name == "info-users":
        flag = False
        for role in ctx.author.roles:
            if role.name == "SaeComp":
                flag = True
        if(flag == True):
            await ctx.channel.send(file=discord.File("users/usersinfo.json"))

    if ctx.content.lower() == "%saiu?" and ctx.channel.name == "saiu-lista":
        flag, filename = runScrapCheck()
        if(flag == True):
            await SearchForTheList()
        else:
            await ctx.channel.send("Ainda não saiu")

    await client.process_commands(ctx)

secret_token = None
try:
    secret_token = os.environ["TOKEN"]
except:
    from secret_keys import TOKEN
    secret_token = TOKEN

client.run(secret_token) 