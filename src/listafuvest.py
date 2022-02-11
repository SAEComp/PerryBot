from typing import Union
import requests
from bs4 import BeautifulSoup

PATH_TO_LIST_NUMBER = "./data/numero_lista.txt"
PATH_TO_PDF = "./data/lista_chamada.pdf"
ACERVO_SUFIX = "fuvest_2022_chamada_"
NEWS_URL = "https://www.fuvest.br/todas-as-publicacoes"
ACERVO_URL = "https://www.fuvest.br/wp-content/uploads/"

def get_html(url: str) -> BeautifulSoup:
    return BeautifulSoup(requests.get(url).text, 'lxml')

def SearchFuvestNews(list_number: int) -> Union[bool, str]:
    html_content = get_html(NEWS_URL)
    
    links = []
    for link in html_content.find_all("a"):
        if( f"{list_number}a-chamada" in link.get("href") and "residencia" not in link.get("href") ):
            links.append(link.get("href"))

    if(len(links) == 0):
        return False, None
    
    # Get all pdf links
    url = links[0]
    pdf_html_content = get_html(url)
    pdf_links = []
    for possible_pdf in pdf_html_content.find_all("a"):
        if(".pdf" in possible_pdf.get("href")):
            pdf_links.append(possible_pdf.get("href"))

    if(len(pdf_links) == 0):
        return False, None

    pdf_url = pdf_links[0]
    response = requests.get(pdf_url)

    with open(PATH_TO_PDF, "wb") as pdf_file:
        pdf_file.write(response.content)
    
    pdf_filename = PATH_TO_PDF.split('/')[-1]

    return True, pdf_filename



def SearchFuvestAcervo(list_number: int) -> Union[bool, str]:
    pdf_url = ACERVO_URL + ACERVO_SUFIX + str(list_number) + ".pdf"
    print(f"Olhando: {pdf_url}")

    response = requests.get(pdf_url)

    if response.status_code == 404: return False, None

    if response.status_code == 200:
        with open(PATH_TO_PDF, "wb") as pdfFile:
            pdfFile.write(response.content)
        return True, PATH_TO_PDF
    
    return False, None


def ReadNumberFile() -> int:

    with open(PATH_TO_LIST_NUMBER) as number_file:
        data_read = number_file.read()
    
    number = int(data_read[0])
    return number

def SearchForFuvest() -> Union[bool, str]:
    
    number = ReadNumberFile()

    flag, pdf_filename = SearchFuvestNews(number)

    return flag, pdf_filename


def SearchIntoAcervoFuvest() -> Union[bool, str]:
    
    number = ReadNumberFile()

    flag, pdf_filename = SearchFuvestAcervo(number)
    
    return flag, pdf_filename


def UpdateListNumber():
    with open(PATH_TO_LIST_NUMBER) as number_file:
        data_read = number_file.read()
    
    number = int(data_read[0])
    number += 1

    with open(PATH_TO_LIST_NUMBER, "w") as number_file:
        number_file.write(str(number))
