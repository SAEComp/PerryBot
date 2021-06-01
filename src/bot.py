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
# #escolher-jogo channel id == 824803055345336330
# #escolher-ano channel id == 812769812861157410
fora_da_ec_message_id = 827227120035954758

#Campeonato bixos
championshipServerID = 831490866119704636
championshipCargosChannelID = 831512528386260993
championshipEmojis = ["💻" , "⚡", "🔩", "⚙", "❌", "🎤"] #EngComp, Eletrica, Mecanica, Mecatronica, Outro, Narrador

#global snakeGame variables
SnakeDict = {
    "lastSnakeMessageId": None,
    "reactionsCounter": [0,0,0,0] ,
    "snake_emojis": ["⬆" , "⬇" , "➡", "⬅"],
    "snakeChannelId": 825497428693745744 #jogo-da-cobrinha channel id
}
wait_time = 120 #minutes


# Request channel variables
requestsChannelDict = {
    "requestChannelOrder": ['016', '017', '018', '019', '020', '021'],
    "categoryID": [832238316387696640, 832238166127149137, 821566511516090428, 821566205239885865, 821566275348070440, 821566366493442108],
    "requestsChannelID": [832238353813471282, 832238243235495986, 832220159598002186, 832220139889098752, 832220124877815848, 832220094050467860],
    "requestsAdminChannelID": 832220500586790943
}

#-------------------------------------------------------------------------------------------
# When the bot logs in
@client.event
async def on_ready():
    print("logged on as ", client.user.name)

    # SearchForTheList.start()

    # Check here the snake game last save in the database ###todo###
    

#-------------------------------------------------------------------------------------------

# Seaches the latest fuvest's list of aproved students
@tasks.loop(minutes=30)
async def SearchForTheList():
    flag, filename = runScrapCheck(list_number=3)
    if(flag == False):
        flag, filename = secretpdf(list_number=3)
    if(flag == True):
        channel = client.get_channel(823653472204226561)
        response = "Saiu a lista de chamada"
        await channel.send(response)
        await channel.send(file=discord.File(filename))
        await channel.send(file=discord.File("names.txt"))
        SearchForTheList.stop()
    else:
        channel = client.get_channel(823721250647441421)
        await channel.send("Acabei de olhar. Ainda não saiu")

#-------------------------------------------------------------------------------------------





@tasks.loop(seconds=wait_time)
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

        game_state, state = game.update(move) #Make the move

        if(game_state == False): #check the game state
            lose_response = "Jogo acabou!\nScore: " + str(game.Length_of_snake - 1)
            await channel.send(lose_response)
            VerifySnakeGame.stop()
            return
    
        if state == "won":
            won_response = "Jogo acabou, você ganhou parabéns!!\nScore: " + str(game.Length_of_snake - 1) + "\nAqui está sua recompensa: " + "https://encurtador.com.br/mqDFM"
            await channel.send(won_response)
            VerifySnakeGame.stop()
            return


        #clear the reaction counter
        SnakeDict["reactionsCounter"] = [0 for _ in range(len(SnakeDict["reactionsCounter"]))]
        
        #get the new matrix and send it
        response_matriz = await StringOfMatriz(game,wait_time)

        message = await channel.send(response_matriz)
        SnakeDict["lastSnakeMessageId"] = message.id
        for emoji in SnakeDict["snake_emojis"]:
            await message.add_reaction(emoji)

    else:
        try:
            message = await channel.fetch_message(SnakeDict["lastSnakeMessageId"])
            response_matriz = await StringOfMatriz(game,wait_time)
            await message.edit(content=response_matriz)
        except:
            pass

#-------------------------------------------------------------------------------------------

@client.command(name="startgame")
async def HandleSnakeGame(ctx, *args):
    if VerifySnakeGame.is_running() == False:
        game = SnakeGame()
        
        if len(args) != 0:
            tempo = int(args[0])
            global wait_time
            wait_time = tempo

        response_matriz = await StringOfMatriz(game,wait_time)
        
        message = await ctx.channel.send(response_matriz)
        SnakeDict["lastSnakeMessageId"] = message.id
        for emoji in SnakeDict["snake_emojis"]:
            await message.add_reaction(emoji)

        VerifySnakeGame.start(game) #comeca a função VerifySnakeGame
        VerifySnakeGame.change_interval(seconds=wait_time)
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
@client.command(name="changetime")
async def ChangeWaitTime(ctx,*args):
    if(len(args) != 0):
        tempo = int(args[0])
        global wait_time
        wait_time = tempo
        VerifySnakeGame.change_interval(seconds=wait_time)
        response = "Tempo mudado para " + str(wait_time) + " segundos."
        await ctx.channel.send(response)
    else:
        await ctx.channel.send("Erro!\n%changetime <tempo>")
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

    if payload.message_id == fora_da_ec_message_id:
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

    #---------------------------------------------------------Requests related------------------------------------------------------
    if payload.channel_id == requestsChannelDict["requestsAdminChannelID"] and payload.user_id != client.user.id:
        guild = client.get_guild(payload.guild_id)

        # Get the content of the message. Name of channel, where and type
        message = await channel.fetch_message(payload.message_id)
        listEmbeds = message.embeds
        embed = listEmbeds[0]
        description = embed.description.splitlines()
        content = [elem.split(':')[1] for elem in description] #Magick
        content[0] = content[0][1:]
        content[1] = content[1].replace(' ', '')
        content[2] = content[2].replace(' ', '')


        #content should be = ['name', 'where', 'type']
        #get the category of the message
        category = None
        requestChannelID = None
        for categoryName, categoryIDIterator, channelIDIterator in zip(requestsChannelDict["requestChannelOrder"], requestsChannelDict["categoryID"], requestsChannelDict["requestsChannelID"]):
            if str(content[1]) == str(categoryName):
                categoryID = categoryIDIterator
                category = discord.utils.get(guild.categories, id=categoryIDIterator)
                requestChannelID = channelIDIterator

        channelToSendResult = client.get_channel(requestChannelID)

        #check if it was approved of denied
        if str(payload.emoji) == "✅":
            response = "Canal "
            # See if event type is to create channel or delete channel
            if embed.title.lower() == "criar":
                if(content[2] == "text"):
                    await guild.create_text_channel(content[0], category=category)
                elif(content[2] == "voice"):
                    await guild.create_voice_channel(content[0], category=category)
                response = str(content[0]) + " aprovado e criado!"
            
            elif embed.title.lower() == "deletar":
                #content should be = ['name', 'where']
                # Get the text channel with content[0] (name)
                for channel in category.channels:
                    print("To printando aqui; " + str(channel.name)) if "teste" in channel.name else None
                    print("Agora to printando o conteudo[0]: " + str(repr(content[0]))) if "teste" in channel.name else None
                    if str(channel.name).lower() == str(content[0]).lower():
                        print("entrei")
                        await channel.delete()
                        response = str(content[0]) + " deletado!"

            # await message.delete(delay=10)
            await channelToSendResult.send(response)
        
        elif(str(payload.emoji) == "❌"):
            await message.delete(delay=10)
            response = "Canal " + str(content[0]) + " rejeitado!"
            await channelToSendResult.send(response)
        
    #---------------------------------------------------------Championship related------------------------------------------------------
    if payload.channel_id == championshipCargosChannelID and payload.guild_id == championshipServerID:
        guild = client.get_guild(championshipServerID)
        member = guild.get_member(payload.user_id)
        message = await channel.fetch_message(payload.message_id)

        if not str(payload.emoji) in championshipEmojis: #if the emoji isnt one of the emojis, remove it
            await message.clear_reaction(payload.emoji)
            return

        #if the user has reacted more than once
        usuario = payload.user_id
        counter = 0
        message_reactions = message.reactions
        flagMoreThenOneReaction = False
        for reaction in message_reactions:
            async for user in reaction.users():
                if usuario == user.id and user.id != client.user.id:
                    counter += 1
                if(counter >= 2):
                    flagMoreThenOneReaction = True
        if flagMoreThenOneReaction:
            for reaction in message_reactions:
                if str(reaction.emoji) == str(payload.emoji):
                    await reaction.remove(member)
                    return



        emoji_added = payload.emoji
        role_id = None
        if str(emoji_added) == str(championshipEmojis[0]): #EngComp
            role_id = 831588091760345169
        elif str(emoji_added) == str(championshipEmojis[1]): #eletrica
            role_id = 831588373088436271
        elif str(emoji_added) == str(championshipEmojis[2]): #mecanica
            role_id = 831588127751012412
        elif str(emoji_added) == str(championshipEmojis[3]): #mecatronica
            role_id = 831588153399836690
        elif str(emoji_added) == str(championshipEmojis[4]): #outro curso
            role_id = 831588910663598091
        elif str(emoji_added) == str(championshipEmojis[5]): #Narrador
            role_id = 831682919834583041

        role_storage = guild.get_role(role_id)
        await member.add_roles(role_storage)




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


    if payload.message_id == fora_da_ec_message_id:
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
        
    #Championship related
    if payload.channel_id == championshipCargosChannelID and payload.guild_id == championshipServerID:
        guild = client.get_guild(championshipServerID)
        member = guild.get_member(payload.user_id)

        emoji_added = payload.emoji
        role_id = None
        if str(emoji_added) == str(championshipEmojis[0]): #EngComp
            role_id = 831588091760345169
        elif str(emoji_added) == str(championshipEmojis[1]): #eletrica
            role_id = 831588373088436271
        elif str(emoji_added) == str(championshipEmojis[2]): #mecanica
            role_id = 831588127751012412
        elif str(emoji_added) == str(championshipEmojis[3]): #mecatronica
            role_id = 831588153399836690
        elif str(emoji_added) == str(championshipEmojis[4]): #outro curso
            role_id = 831588910663598091
        elif str(emoji_added) == str(championshipEmojis[5]): #Narrador
            role_id = 831682919834583041

        role_storage = guild.get_role(role_id)
        await member.remove_roles(role_storage)







@client.command(name="champroles")
async def ChampionshipRolesManipulation(ctx, *args):
    guild = client.get_guild(championshipServerID)
    if guild.id != championshipServerID: return

    channel = client.get_channel(championshipCargosChannelID)

    embed = discord.Embed(title="Escolha seu curso", description="💻:    EngComp\n⚡:    Elétrica\n🔩:    Mecânica\n⚙:    Mecatrônica\n❌:    Outro curso\n🎤: Narrador")
    message = await channel.send(embed=embed)
    for emoji in championshipEmojis:
        await message.add_reaction(emoji)




           
            
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


#------------------------------------------------------------------------------------------------------------------------------------------------------
                                            ### REQUESTS TO CREATE/DELETE ANOTHER CHANNEL ###

@client.command(name="request")
async def HandleRequestsInput(ctx, *, args):
    # Request's input should be %request create/delete <name> <type=text(default)>
    # When the request is made, it will be sent to the admin category waiting for the approval of anyone from SaeComp
    # Reactions types: ✅ ❌
    # The message sent to the admin panel will be an embed and have the <name> of the new channel as a title, 
    # where it was made, 018,019,020,021,etc. And it's <type> text by default or channel if specified
    
    
    # Check if the request was made from one of the requests channels.
    if ctx.channel.id not in requestsChannelDict["requestsChannelID"]:
        await ctx.channel.send("Este comando só pode ser usado em um dos canais de requests.")
        return


    requestInput = args.split(' ')
    wrong_format = "Formato errado! Digite %request help"
    

    if(requestInput[0].lower() == "create"): # Handle creation of channels
        requestInput.pop(0) # Remove Create word
        if (len(requestInput) == 0):
            await ctx.channnel.send(wrong_format)
            return

        # Verify if the last pos has the input type
        lastpos = requestInput[len(requestInput)-1]
        channelType = "text"
        if(lastpos.lower() == "text" or lastpos.lower() == "voice"):
            #if it has check if its voice
            if(lastpos.lower() == "voice"):
                channelType = "voice"
        #then discard the last element of the list
        requestInput.pop()

        if(len(requestInput) == 0):
            await ctx.channel.send(wrong_format)
            return

        channelName =  ' '.join(requestInput)


        # Verify if the name of the requested channel already exists.
        channelTheMessageWasSent = ctx.channel
        categoryOfMessageSent = channelTheMessageWasSent.category
        for channelInCategory in categoryOfMessageSent.channels:
            if channelName.lower() == channelInCategory.name.lower():
                await ctx.channel.send("Ação inválida, canal já existe!")
                return

        # Now send to the requests-admin channel
        title = "Criar"
        description = "Criar canal com nome: " + str(channelName) + "\nEstá sendo criado na categoria: " + str(categoryOfMessageSent) + "\nTipo: " + str(channelType)

        embed = discord.Embed(title=title, description=description)

        requestAdminChannel = client.get_channel(requestsChannelDict["requestsAdminChannelID"])
        messageAdmin = await requestAdminChannel.send(embed=embed)
        await messageAdmin.add_reaction("✅")        
        await messageAdmin.add_reaction("❌")        
        await ctx.channel.send("Pedido feito! Espere ser aprovado por alguem da SAEComp")

        return

    
    elif(requestInput[0].lower() == "delete"): # Handle removal of channels
        requestInput.pop(0) #remove delete word
        if(len(requestInput) == 0):
            await ctx.channnel.send(wrong_format)
            return
    
        # Verify if the last pos has the input type
        lastpos = requestInput[len(requestInput)-1]
        channelType = "text"
        if(lastpos.lower() == "text" or lastpos.lower() == "voice"):
            #if it has check if its voice
            if(lastpos.lower() == "voice"):
                channelType = "voice"
        #then discard the last element of the list
        requestInput.pop()

        if(len(requestInput) == 0):
            await ctx.channel.send(wrong_format)
            return
            
        channelName =  ' '.join(requestInput) if channelType == "voice" else '-'.join(requestInput)

        # Verify if the channel exists
        doesChannelExists = False
        channelTheMessageWasSent = ctx.channel
        categoryOfMessageSent = channelTheMessageWasSent.category
        for channelInCategory in categoryOfMessageSent.channels:
            if channelName.lower() == channelInCategory.name.lower():
                doesChannelExists = True

        if doesChannelExists:
            # Create the message to delete certain channel
            title = "Deletar" 
            description = description = "Deletando canal com nome: " + str(channelName) + "\nEstá sendo deletado na categoria: " + str(categoryOfMessageSent) + "\nTipo: " + str(channelType)
            embed = discord.Embed(title=title, description=description)
            requestAdminChannel = client.get_channel(requestsChannelDict["requestsAdminChannelID"])
            messageAdmin = await requestAdminChannel.send(embed=embed)
            await messageAdmin.add_reaction("✅")        
            await messageAdmin.add_reaction("❌")
            await ctx.channel.send("Pedido feito! Espere ser aprovado por alguem da SAEComp")
        
        else:
            await ctx.channel.send("Esse canal não existe.")
        
        return

    elif(requestInput[0].lower() == "help"):
        helpResponse = "Para pedir um canal de texto ou voz use o comando:\n%request <create/delete> <nome> <tipo>\nO <tipo> pode ser TEXT ou VOICE. Se não for especificado será criado como um canal de texto."
        await ctx.channel.send(helpResponse)
        return
    
#------------------------------------------------------------------------------------------------------------------------------------------------------










@client.event
async def on_message(ctx):
    
    if ctx.author == client.user:
        return

    # if ctx.content.lower() == "%send extras" and ctx.channel.name == "extras" and ctx.author.name == "Franreno":
    #     from getextra import extras_name, extras_description, extras_image_name
    #     for name,desc,img_name in zip(extras_name, extras_description, extras_image_name):
    #         embed = discord.Embed(title=name, description=desc)
    #         img_path = "src/imgs/" + str(img_name)
    #         file = discord.File(img_path)
    #         await ctx.channel.send(embed=embed, file=file)

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
        flag, filename = runScrapCheck(list_number=3)
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