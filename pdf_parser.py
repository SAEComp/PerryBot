import pdfreader, json
from pdfreader import PDFDocument, SimplePDFViewer

def sameFistLetter(text):
    if(len(text) < 30):
        return False
    
    if text[0] == text[1] and text[0] == text[2] and text[0] == text[3] and text[0] == text[4]:
        return True
    else:
        return False

def deInText(text):
    if(len(text) < 3):
        return False
    if text[0] == "D" and text[1] == "e" and text[2] == ' ':
        return True
    else:
        return False

def getNames(filename):
    fd = open(filename , "rb")
    doc = PDFDocument(fd)
    viewer = SimplePDFViewer(fd)

    info = {
        "nomes": [],
        "cpf": [],
        "curso": []
    }

    c = 1
    for canvas in viewer:
        page_strings = canvas.strings
        string_list = []    
        for text in page_strings:
            if(sameFistLetter(text) == False and "Chamada" not in text and "Lista de Publicação" not in text and "FUVEST" not in text and len(text) != 1):
                if text != "NOME" and text != "CPF" and text != "CURSO" and "/34" not in text and "Até" not in text and deInText(text) == False:
                    string_list.append(text)


        counter = 0
        for text in string_list:

            if(counter == 0):
                info["nomes"].append(text)

            if(counter == 1):
                info["cpf"].append(text)

            if(counter == 2):
                info["curso"].append(text)
            
            if(counter == 2):
                counter = 0
            else:
                counter += 1

        print("Read page " + str(c))
        c += 1



    howmuch = 0
    with open("names.txt" , "w") as f:
        for nome,cpf,curso in zip(info["nomes"], info["cpf"], info["curso"]):
            if curso == "765−21":
                howmuch += 1
                response = str(nome) + '\n'
                print(nome + ' ' + curso )
                f.write(response)
        
        f.close()

        print(howmuch)
        
    fd.close()
