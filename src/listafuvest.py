import requests, time
from bs4 import BeautifulSoup
from pdf_parser import getNames


def getHTML(url):
    html_content = requests.get(url).text
    soup = BeautifulSoup(html_content, 'lxml')
    
    return soup

def runScrapCheck():
    url = "https://www.fuvest.br/category/noticias/"
    soup = getHTML(url)

    #get all href links, and search for the 1st list
    links = [link.get("href") for link in soup.find_all("a") if "2a-chamada" in link.get("href")] 

    #verify if there is something on the list
    if(len(links) > 0):
        #get the pdf
        url = links[0]
        soup = getHTML(url)
        pdf_link = [pdf.get("href") for pdf in soup.find_all("a") if ".pdf" in pdf.get("href")]
        #if there is a pdf then
        if(len(pdf_link) > 0):
            #downlaod and save the pdf
            url = pdf_link[0]
            response = requests.get(url)
            with open("lista_chamada.pdf" , "wb") as f:
                f.write(response.content)
                f.close()
            filename = "lista_chamada.pdf"
            getNames(filename)
            return True, filename
        
    return False, None

def secretpdf(list_number):
    url = "https://acervo.fuvest.br/fuvest/2021/fuvest_2021_chamada_" + str(list_number) + ".pdf"
    response = requests.get(url)
    if response.status_code == 404: return False, None
    elif response.status_code == 200:
        filename = "lista_chamada.pdf"
        with open(filename , "wb") as f:
            f.write(response.content)
            f.close()
        getNames(filename)
        return True, filename
    else:
        return False, None
