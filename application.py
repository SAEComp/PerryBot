import json
import os

def removeGarbage(message):
    get_user = message.split(":")
    get_user[0] = get_user[0].replace('*' , '')
    # get_user[0] = get_user[0].replace(' ' , '')
    # get_user[1] = get_user[1].replace(' ', '')

    return get_user

def app(message, author):
    users = []
    
    splited = message.split(',')


    for content in splited:
        if ':' in content:
            get_user = removeGarbage(content)
            info = {
                "platform": get_user[0],
                "user": get_user[1]
            }
            users.append(info)

    return 1, users


def parseResponse(users, author):
    ret = "Obrigado " + author.mention +"! Por favor confira.\n\n"
    for user in users:
        ret += "Plataforma: " + user["platform"] + " -> " + "User: " + user["user"] + "\n"
    
    ret += "\nCaso esteja errado apenas digite novamente\nCaso deseje remover digite '*remover'"

    return ret

def writeInfo(content, author):
    info = {
        "platforms": [],
        "users": []
    }

    for x in content:
        info["platforms"].append(x["platform"])
        info["users"].append(x["user"])


    with open("users/usersinfo.json" , "r") as f:
        data = json.load(f)
        f.close()
    flag, garbage = doesUserExits(author.name)

    #if the user is a new addition
    if(flag == False):
        data["authors"].append(author.name)
        if(author.nick == None):
            data["discordnicknames"].append("Nao tem apelido")
        else:
            data["discordnicknames"].append(author.nick)
        data["id"].append(author.id)
        data["authors_platforms"].append(info["platforms"])
        data["authors_users"].append(info["users"])

    #only to update certain user info, beacuse it already exist
    elif(flag == True):
        pos = 0
        for x,y,z in zip(data["authors"], data["authors_platforms"], data["authors_users"]):
            if x.lower() == author.name.lower():
                data["authors_platforms"].remove(y)
                data["authors_platforms"].insert(pos, info["platforms"])
                data["authors_users"].remove(z)
                data["authors_users"].insert(pos, info["users"])
            pos += 1
        
    with open("users/temp.json" , "w") as temp:
        json.dump(data, temp)
        temp.close()

    os.remove("users/usersinfo.json")
    os.rename("users/temp.json" , "users/usersinfo.json")
            

def removeInfo(author):

    with open("users/usersinfo.json" , "r") as f:
        data = json.load(f)
        f.close()

    name = author.name
    for x,y,z,w,d in zip(data["authors"], data["discordnicknames"], data["id"], data["authors_platforms"], data["authors_users"]):
        if x == name:
            data["authors"].remove(x)
            data["discordnicknames"].remove(y)
            data["id"].remove(z)
            data["authors_platforms"].remove(w)
            data["authors_users"].remove(d)

    with open("users/temp.json", "w") as temp:
        json.dump(data, temp)
        temp.close()

    os.remove("users/usersinfo.json")
    os.rename("users/temp.json", "users/usersinfo.json")

        
def doesUserExits(user):
    with open("users/usersinfo.json" , "r") as f:
        data = json.load(f)
        f.close()
    
    for x,y in zip(data["authors"], data["discordnicknames"]):
        if x.lower() == user.lower() or y.lower() == user.lower():
            return True, x
    
    return False, None
        

def getInfoFromUser(user):

    with open("users/usersinfo.json" , "r") as f:
        data = json.load(f)
        f.close()

    info_from_user = {}

    for x,y,z,w,d in zip(data["authors"], data["discordnicknames"], data["id"], data["authors_platforms"], data["authors_users"]):
        if x == user:
            info_from_user["authors"] = x
            info_from_user["discordnicknames"] = y
            info_from_user["id"] = z
            info_from_user["authors_platforms"] = w
            info_from_user["authors_users"] = d

    # print(info_from_user)

    ret = "Informações sobre o usuário:\nNome: " + str(info_from_user["authors"]) + '\n'
    if(info_from_user["discordnicknames"] != "Nao tem apelido"):
        ret += "Apelido: " + str(info_from_user["discordnicknames"]) + "\n"
    for x,y in zip(info_from_user["authors_platforms"], info_from_user["authors_users"]):
        ret += "Plataforma: " + str(x) + " -> Username: " + str(y) + '\n'

    return ret


def getInfoFromAllUsers():
    with open("users/usersinfo.json" , "r") as f:
        data = json.load(f)
        f.close()

    with open("users/getAllInfo.txt" , "w") as f:
        write_str = str()
        for x,y,z,w,d in zip(data["authors"], data["discordnicknames"], data["id"], data["authors_platforms"], data["authors_users"]):
            write_str += "Nome do usuário: " + str(x) + '\n'
            if(y != "Nao tem apelido"):
                write_str += "Apelido: " + str(y) + '\n'
            #write the platforms that the user has written.
            #w == list of platforms, d == list of users. 
            for a,b in zip(w,d):
                write_str += "Plataforma: " + str(a) + "  ->  Usuário: " + str(b) + '\n'
            
            write_str += '\n----------------------------------\n\n\n'
        
        f.write(write_str)
        f.close()
    
    return 1


