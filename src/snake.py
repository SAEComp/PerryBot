import random, discord, datetime

class SnakeGame():
    def __init__(self):
        
        self.cod_blank = 0
        self.cod_alimento = 1
        self.cod_snake_body = 2
        self.cod_snake_head = 3

        self.gridSize = 6
        self.cellSize = 1

        self.matriz = []
        for i in range(0, self.gridSize):
            self.matriz.append([])
            for _ in range(0, self.gridSize):
                self.matriz[i].append(0)

        self.game_over = False
        self.game_close = False
    
    #spawna a cabeça da snake
        self.x_snake = random.randrange(0, self.gridSize - self.cellSize)
        self.y_snake = random.randrange(0, self.gridSize - self.cellSize)

        self.x_snake_change = 0
        self.y_snake_change = 0

        self.snake_List = []
        self.Length_of_snake = 1
        self.foodx = random.randrange(0, self.gridSize - self.cellSize)
        self.foody = random.randrange(0, self.gridSize - self.cellSize)

        #spawna o alimento
        if self.x_snake == self.foodx and self.y_snake == self.foody:
            flagOk = False

            while not flagOk:
                self.foodx = random.randrange(0, self.gridSize - self.cellSize)
                self.foody = random.randrange(0, self.gridSize - self.cellSize)

                for body in self.snake_List:
                    if body[0] == self.foodx and body[1] == self.foody: 
                        flagOk = False
                        break
                    else:
                        flagOk = True

        self.setAllBlank()
        self.setAlimento(self.foodx, self.foody)
        self.setSnakeHeadInicial(self.x_snake, self.y_snake)
        

    def update(self, keyPressed):
        
        # self.printMatrix_Fran()

        if keyPressed == "a":
            self.x_snake_change = -self.cellSize
            self.y_snake_change = 0
        elif keyPressed == "d":
            self.x_snake_change = self.cellSize
            self.y_snake_change = 0
        elif keyPressed == "w":
            self.x_snake_change = 0
            self.y_snake_change = -self.cellSize
        elif keyPressed == "s":
            self.x_snake_change = 0
            self.y_snake_change = self.cellSize
        else:
            keyPressed = "null"
            self.x_snake_change = 0
            self.y_snake_change = 0

        #atualiza o x e y da cobrita
        self.x_snake += self.x_snake_change
        self.y_snake += self.y_snake_change

        #verifica se bateu a cabeça na parede
        if self.x_snake >= self.gridSize or self.x_snake < 0 or self.y_snake >= self.gridSize or self.y_snake < 0:
            self.game_over = True
            self.perderJogo()
            return False

        ################# 
        snake_Head = []
        snake_Head.append(self.x_snake)
        snake_Head.append(self.y_snake)
        self.snake_List.append(snake_Head)
        if len(self.snake_List) > self.Length_of_snake:
            del self.snake_List[0]

        #checa colisão do corpo da cobra com a cabeça
        for x in self.snake_List[:-1]:
            if x == snake_Head:
                game_over = True
                self.perderJogo()
                return False
    
        
        #desenha o fundo
        self.setAllBlank()

        #desenha a comida
        self.setAlimento(int(self.foodx), int(self.foody))
        
        #atualiza a cobra na matriz
        self.setSnakeBody(self.snake_List)
        self.setSnakeHead(self.snake_List, snake_Head)

        # printa o score
        # self.print_score(self.Length_of_snake - 1)

        # printa a matriz no terminal
        # self.printMatrix_Fran()

        # se ele comer
        if self.x_snake == self.foodx and self.y_snake == self.foody:
            flagOk = False

            while not flagOk:
                self.foodx = random.randrange(0, self.gridSize - self.cellSize)
                self.foody = random.randrange(0, self.gridSize - self.cellSize)
                
                for body in self.snake_List:
                    if body[0] == self.foodx and body[1] == self.foody: 
                        flagOk = False
                        break
                    else:
                        flagOk = True
                    
            self.Length_of_snake += 1
            self.setAlimento(self.foodx,self.foody)
        return True

    def perderJogo(self):
        print("Perdestes?!?!?")
        self.print_score(self.Length_of_snake - 1)

    def get_matriz(self):
        return self.matriz
    
    ### funções a mais
    def print_score(self, score):
        print("Your Score: " + str(score))
        return score
        
    def printMatrix_Fran(self):
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                print(self.matriz[x][y] , end=' ')
            
            print('\n', end='')

    def setAllBlank(self):
        for x in range(self.gridSize):
            for y in range(self.gridSize):
                self.matriz[x][y] = self.cod_blank

    # eu tive que inverter o x com o y
    def setAlimento(self, foodx, foody):
        self.matriz[foody][foodx] = self.cod_alimento

    # eu tive que inverter o x com o y
    def setSnakeBody(self, snake_List):
        for body in snake_List:
            self.matriz[int(body[1])][int(body[0])] = self.cod_snake_body

    # eu tive que inverter o x com o y
    def setSnakeHead(self, snake_List, snake_Head):
        for body in snake_List:
            if body == snake_Head:
                self.matriz[int(body[1])][int(body[0])] = self.cod_snake_head

    def setSnakeHeadInicial(self, x_snake, y_snake):
        self.matriz[y_snake][x_snake] = self.cod_snake_head


    def ReloadSaveState(self, loaded_save_state):
        self.matriz = loaded_save_state[1]
        # self.snake_List = loaded_save_state[2]
        # self.foodx = loaded_save_state[3][1]
        # self.foodx = loaded_save_state[3][0]



def VerifyMatriz(value):
    if value == 0:
        return "⬜"
    elif value == 1:
        return "🍎"
    elif value == 2:
        return "🟨"
    elif value == 3:
        return "😃"
    else:
        return None

async def GetLastSnakeMessageId(client, channel_id):

    channel = client.get_channel(channel_id)
    async for message in channel.history(limit=10):
        if message.author.id == client.user.id and "⬜" in message.content and "😃" in message.content:
            return message.id

def GetCurrentTime(wait_time):
    current_time = datetime.datetime.now()
    minutos = current_time.minute
    hora = current_time.hour
    hora -= 3 #Diferent time zones
    if( (minutos + wait_time) >= 60):
        minutos = (minutos + wait_time) - 60
        hora += 1
    else:
        minutos += wait_time

    return [hora, minutos]

async def StringOfMatriz(game,wait_time):

    # tempo = GetCurrentTime(wait_time)

    response_matriz = "Score: " + str(game.Length_of_snake - 1) + '\n'
    for x in range(game.gridSize):
        for y in range(game.gridSize):
            response_matriz += VerifyMatriz(game.matriz[x][y]) + '  '
        response_matriz += '\n'

    ret = "O jogo vai progredir em " + str(wait_time) + " segundos\n" + response_matriz
    return ret

def GetSnakeValuesBack(save_state):   
    #transform string of matriz back to a real matriz
    gridSize = int(save_state[1])
    string_matriz = save_state[2]
    string_snakeList = save_state[3]
    string_food = save_state[4]
    
    matriz = []
    for x in range(gridSize):
        helper = []
        for y in range(gridSize):
            helper.append(int(string_matriz[x*gridSize+y]))
        matriz.append(helper)
    
    #need to get the snake list back
    list_snakeList = string_snakeList.split(' ')
    snakeList = []
    helper = []
    for x in range(len(list_snakeList)-1):
        print(list_snakeList[x][0])
        helper.append(int(list_snakeList[x][0]))
        helper.append(int(list_snakeList[x][1]))
        snakeList.append(helper)
        helper = []

    #need to get the food back
    food_pos = []
    food_pos.append(int(string_food[0]))
    food_pos.append(int(string_food[2]))

    return [gridSize, matriz, snakeList, food_pos]


def CreateSaveState(game):
    save_state = []
    
    #create a matrix instance to save
    string_matriz = str()
    for x in range(game.gridSize):
        for y in range(game.gridSize):
            string_matriz += str(game.matriz[x][y])

    #Create a snakelist instance to save
    snakeList = game.snake_List
    string_snakeList = str()
    if(len(snakeList) != 0):
        for x in range(len(snakeList)):
            string_snakeList += str(snakeList[x][0])
            string_snakeList += str(snakeList[x][1]) + ' '

    #food
    string_food = str(game.foodx) + ' ' + str(game.foody)
    
    save_state.append(1) #game_state: 1 is running, 0 not running
    save_state.append(game.gridSize) #matrix grid size
    save_state.append(string_matriz) #matrix in one line
    save_state.append(string_snakeList) #position of snake
    save_state.append(string_food) #pos of food

    return save_state