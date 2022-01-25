import fitz

# o traco − eh um caractere especial de unicode: U+2212!
COURSE_CODE = '765−21'


PATH_TO_PDF = "./data/lista_chamada.pdf"
OUTPUT_PATH = "./data/nomes.txt"


LIST_OF_UNWANTED_WORDS = ["Chamada", "Lista de Publicação", "FUVEST", "NOME", "CPF", "CURSO", "Até", "De"]

def get_raw_text() -> str:
    with fitz.open(PATH_TO_PDF) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def contains_word(text: str, word: str) -> bool:
    return ( ' ' + word + ' ' ) in ( ' ' + text + ' ' )


def isAllSameLetter(text: str) -> bool:
    first_letter = text[0]
    amount = 0
    for char in text:
        if(char == first_letter):
            amount += 1
    
    return amount == len(text)


def remove_unwanted_words(raw_text: str) -> list:
    parsed_text = []
    splited_raw_text = raw_text.split('\n')

    for line in splited_raw_text:
        if( len(line) == 1 or len(line) == 0 or '/' in line): 
            continue

        unwanted_word_flag = False
        for unwanted_word in LIST_OF_UNWANTED_WORDS:
            if( contains_word(line, unwanted_word) or isAllSameLetter(line)):
                unwanted_word_flag = True
                break

        if(unwanted_word_flag):
            continue
        
        parsed_text.append(line)
    
    return parsed_text


def create_list_with_students(parsed_text: list) -> list:
    # [nome, 'cpf code'].
    # Verificar se tem numero no texto.
    # Se tiver eh um cpf-code.
    # Se nao tiver eh um nome.
    students_list = []
    student_name = ""
    student_cpf_code = ""
    for element in parsed_text:
        
        # Verificar se tem numero no elemento
        if( any( char.isdigit() for char in element) == False ):
            # eh o nome do aluno
            student_name = element
            continue
        else:    
            student_cpf_code = element

        if(student_cpf_code.split(" ")[1] == COURSE_CODE ):
            students_list.append(student_name + " " + student_cpf_code)
            student_name = ""
            student_cpf_code = ""

    return students_list


def ParsePDF() -> bool:
    raw_text = get_raw_text()
    parsed_text = remove_unwanted_words(raw_text)
    students_list = create_list_with_students(parsed_text)
   
    if(len(students_list) == 0): 
        return False

    with open(OUTPUT_PATH, "w") as output_file:
        output_file.write("Nomes:\n")
        for student in students_list:
            output_file.write(student + '\n')
    
    return True
        