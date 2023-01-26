# Request channel variables
# requestsChannelDict = {
#     "requestChannelOrder": ['016', '017', '018', '019', '020', '021', '🎮Jogos'],
#     "categoryID": [832238316387696640, 832238166127149137, 821566511516090428, 821566205239885865, 821566275348070440, 821566366493442108, 812795327752831056],
#     "requestsChannelID": [832238353813471282, 832238243235495986, 832220159598002186, 832220139889098752, 832220124877815848, 832220094050467860, 862073690924646450],
#     "requestsAdminChannelID": 832220500586790943
# }

# REMOVENDO PROCURA DA LISTA DA FUVEST
# @tasks.loop(minutes=30)
# async def SearchForTheList():
#     print("Procurando a lista")
#     flag, filename = SearchForFuvest()
#     if (flag == False):
#         print("Nao saiu no site de noticias")
#         flag, filename = SearchIntoAcervoFuvest()

#     if (flag == True):
#         print("SAIU")
#         ParsePDF()
#         channel = client.get_channel(LISTA_FUVEST_CHANNEL_ID)
#         response = "Saiu a lista de chamada!"
#         await channel.send(response)
#         await channel.send(file=discord.File(filename))
#         await channel.send(file=discord.File("./data/names.txt"))
#         UpdateListNumber()
#         SearchForTheList.stop()
#     else:
#         print("Nao saiu.")
#         # channel = client.get_channel(823721250647441421)
#         # await channel.send("Acabei de olhar! Ainda não saiu :(")

# ---------------------------------------------------------Requests related------------------------------------------------------
# if payload.channel_id == requestsChannelDict["requestsAdminChannelID"] and payload.user_id != client.user.id:
#     guild = client.get_guild(payload.guild_id)

#     # Get the content of the message. Name of channel, where and type
#     message = await channel.fetch_message(payload.message_id)
#     listEmbeds = message.embeds
#     embed = listEmbeds[0]
#     description = embed.description.splitlines()
#     content = [elem.split(':')[1] for elem in description]  # Magick
#     content[0] = content[0][1:]
#     content[1] = content[1].replace(' ', '')
#     content[2] = content[2].replace(' ', '')

#     # content should be = ['name', 'where', 'type']
#     # get the category of the message
#     category = None
#     requestChannelID = None
#     for categoryName, categoryIDIterator, channelIDIterator in zip(requestsChannelDict["requestChannelOrder"], requestsChannelDict["categoryID"], requestsChannelDict["requestsChannelID"]):
#         if str(content[1]) == str(categoryName):
#             categoryID = categoryIDIterator
#             category = discord.utils.get(
#                 guild.categories, id=categoryIDIterator)
#             requestChannelID = channelIDIterator

#     channelToSendResult = client.get_channel(requestChannelID)

#     # check if it was approved of denied
#     if str(payload.emoji) == "✅":
#         response = "Canal "
#         # See if event type is to create channel or delete channel
#         if embed.title.lower() == "criar":
#             if (content[2] == "text"):
#                 await guild.create_text_channel(content[0], category=category)
#             elif (content[2] == "voice"):
#                 await guild.create_voice_channel(content[0], category=category)
#             response = str(content[0]) + " aprovado e criado!"

#         elif embed.title.lower() == "deletar":
#             # content should be = ['name', 'where']
#             # Get the text channel with content[0] (name)
#             for channel in category.channels:
#                 if str(channel.name).lower() == str(content[0]).lower():
#                     await channel.delete()
#                     response = str(content[0]) + " deletado!"

#         await message.delete(delay=10)
#         await channelToSendResult.send(response)

#     elif (str(payload.emoji) == "❌"):
#         await message.delete(delay=10)
#         response = "Canal " + str(content[0]) + " rejeitado!"
#         await channelToSendResult.send(response)


# -------------------------------------------------------------------------------------------

# random messages handling
# @client.command(name="random")
# async def HandleRandomEvents(ctx, *args):

#     largs = list(args)

#     if (len(largs) == 0):
#         # send here the random message

#         flag = False
#         while flag == False:
#             try:
#                 ret = get_random_text()
#             except:
#                 pass

#             if ret != lastTwoRandomMessages[0]:
#                 flag = True
#                 lastTwoRandomMessages[1] = lastTwoRandomMessages[0]
#                 lastTwoRandomMessages[0] = ret
#                 break

#         await ctx.channel.send(ret)

#     elif (largs[0] == "add"):
#         # add the message into the database
#         largs.pop(0)
#         if (len(largs) == 0):
#             await ctx.channel.send("Formato errado digite %random help")
#             return

#         # add data
#         new_message = ' '.join(largs)

#         try:
#             add_random_text(new_message)
#         except:
#             await ctx.channel.send("Essa mensagem já existe")
#             return

#         response = new_message + " adicionado!"
#         await ctx.channel.send(response)

#     elif (largs[0] == "remove"):
#         largs.pop(0)
#         if (len(largs) == 0):
#             await ctx.channel.send("Formato errado digite %random help")
#             return

#         message_to_remove = ' '.join(largs)

#         try:
#             remove_random_text(message_to_remove)
#         except:
#             await ctx.channel.send("Mensagem inexistente")
#             return

#         await ctx.channel.send("Mensagem removida")

#     elif (largs[0] == "help"):
#         response = "    ->%random: para uma mensagem aleatoria\n->%random add [mensagem]: adiciona a mensagem digitada\n->%random remove [mensagem]: remove a mensagem digitada"
#         await ctx.channel.send(response)

#     # list all the messages ###MUST BE USED WITH CAUTION###
#     elif (largs[0] == "list"):
#         flag = False
#         for role in ctx.author.roles:
#             if role.name == "SaeComp":
#                 flag = True
#         if (flag == True):
#             all_text = get_all_text()
#             for text in all_text:
#                 await ctx.channel.send(text[0])
#     else:
#         response = "Formato errado\n    ->%random: para uma mensagem aleatoria\n    ->%random add [mensagem]: adiciona a mensagem digitada\n    ->%random remove [mensagem]: remove a mensagem digitada"
#         await ctx.channel.send(response)


# # ------------------------------------------------------------------------------------------------------------------------------------------------------
#         ### REQUESTS TO CREATE/DELETE ANOTHER CHANNEL ###

# @client.command(name="request")
# async def HandleRequestsInput(ctx, *, args):
#     # Request's input should be %request create/delete <name> <type=text(default)>
#     # When the request is made, it will be sent to the admin category waiting for the approval of anyone from SaeComp
#     # Reactions types: ✅ ❌
#     # The message sent to the admin panel will be an embed and have the <name> of the new channel as a title,
#     # where it was made, 018,019,020,021,etc. And it's <type> text by default or channel if specified

#     # Check if the request was made from one of the requests channels.
#     if ctx.channel.id not in requestsChannelDict["requestsChannelID"]:
#         await ctx.channel.send("Este comando só pode ser usado em um dos canais de requests.")
#         return

#     requestInput = args.split(' ')
#     wrong_format = "Formato errado! Digite %request help"

#     if (requestInput[0].lower() == "create"):  # Handle creation of channels
#         requestInput.pop(0)  # Remove Create word
#         if (len(requestInput) == 0):
#             await ctx.channnel.send(wrong_format)
#             return

#         # Verify if the last pos has the input type
#         lastpos = requestInput[len(requestInput)-1]
#         channelType = "text"
#         if (lastpos.lower() == "text" or lastpos.lower() == "voice"):
#             # if it has check if its voice
#             if (lastpos.lower() == "voice"):
#                 channelType = "voice"
#         # then discard the last element of the list
#         requestInput.pop()

#         if (len(requestInput) == 0):
#             await ctx.channel.send(wrong_format)
#             return

#         channelName = ' '.join(requestInput)

#         # Verify if the name of the requested channel already exists.
#         channelTheMessageWasSent = ctx.channel
#         categoryOfMessageSent = channelTheMessageWasSent.category
#         for channelInCategory in categoryOfMessageSent.channels:
#             if channelName.lower() == channelInCategory.name.lower():
#                 await ctx.channel.send("Ação inválida, canal já existe!")
#                 return

#         # Now send to the requests-admin channel
#         title = "Criar"
#         description = "Criar canal com nome: " + \
#             str(channelName) + "\nEstá sendo criado na categoria: " + \
#             str(categoryOfMessageSent) + "\nTipo: " + str(channelType)

#         embed = discord.Embed(title=title, description=description)

#         requestAdminChannel = client.get_channel(
#             requestsChannelDict["requestsAdminChannelID"])
#         messageAdmin = await requestAdminChannel.send(embed=embed)
#         await messageAdmin.add_reaction("✅")
#         await messageAdmin.add_reaction("❌")
#         await ctx.channel.send("Pedido feito! Espere ser aprovado por alguem da SAEComp")

#         return

#     elif (requestInput[0].lower() == "delete"):  # Handle removal of channels
#         requestInput.pop(0)  # remove delete word
#         if (len(requestInput) == 0):
#             await ctx.channnel.send(wrong_format)
#             return

#         # Verify if the last pos has the input type
#         lastpos = requestInput[len(requestInput)-1]
#         channelType = "text"
#         if (lastpos.lower() == "text" or lastpos.lower() == "voice"):
#             # if it has check if its voice
#             if (lastpos.lower() == "voice"):
#                 channelType = "voice"
#         # then discard the last element of the list
#         requestInput.pop()

#         if (len(requestInput) == 0):
#             await ctx.channel.send(wrong_format)
#             return

#         channelName = ' '.join(
#             requestInput) if channelType == "voice" else '-'.join(requestInput)

#         # Verify if the channel exists
#         doesChannelExists = False
#         channelTheMessageWasSent = ctx.channel
#         categoryOfMessageSent = channelTheMessageWasSent.category
#         for channelInCategory in categoryOfMessageSent.channels:
#             if channelName.lower() == channelInCategory.name.lower():
#                 doesChannelExists = True

#         if doesChannelExists:
#             # Create the message to delete certain channel
#             title = "Deletar"
#             description = description = "Deletando canal com nome: " + \
#                 str(channelName) + "\nEstá sendo deletado na categoria: " + \
#                 str(categoryOfMessageSent) + "\nTipo: " + str(channelType)
#             embed = discord.Embed(title=title, description=description)
#             requestAdminChannel = client.get_channel(
#                 requestsChannelDict["requestsAdminChannelID"])
#             messageAdmin = await requestAdminChannel.send(embed=embed)
#             await messageAdmin.add_reaction("✅")
#             await messageAdmin.add_reaction("❌")
#             await ctx.channel.send("Pedido feito! Espere ser aprovado por alguem da SAEComp")

#         else:
#             await ctx.channel.send("Esse canal não existe.")

#         return

#     elif (requestInput[0].lower() == "help"):
#         helpResponse = "Para pedir um canal de texto ou voz use o comando:\n%request <create/delete> <nome> <tipo>\nO <tipo> pode ser TEXT ou VOICE. Se não for especificado será criado como um canal de texto."
#         await ctx.channel.send(helpResponse)
#         return

# ------------------------------------------------------------------------------------------------------------------------------------------------------
