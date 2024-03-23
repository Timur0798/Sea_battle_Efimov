from random import randint
import time

#создание класса точки-координаты
class Coord:
    def __init__(self,x,y):
        self.x=x
        self.y=y

    # метод для возможности сравнения точек-координат. проверки вхождения и т.д.
    def __eq__(self, other):
        return (self.x==other.x) and (self.y==other.y)

    # строчное представление метода
    def __repr__(self):
        return f"Coord({self.x}, {self.y})"


# создание классов исключений
# общий класс исключений
class BoardException(Exception):
    pass

class OutOfBoardEx(BoardException):
    def __str__(self):
        return("Выстрел за пределы поля")

class BusyCoordEx(BoardException):
    def __str__(self):
        return("В эту точку уже стреляли")

# неверное размещение корабля
class ShipWrongAccomodationEx(BoardException):
    pass

# создание класса корабля
class Ship():
    def __init__(self,bow,len,orient): # скроем параметры с помощью инкапсуляции
        self.__bow=bow
        self.__len=len
        self.__orient=orient
        self.__lives = len

    # создание свойства параметра lives и его сеттера для инкапсуляции
    @property
    def lives(self):
        return self.__lives

    @lives.setter
    def lives(self,len):
        self.__lives = len

    # метод для размещения корабля горизотально или вертикально
    @property
    def coords(self):
        ship_coords=[]
        for i in range(self.__len):
            start_x=self.__bow.x
            start_y=self.__bow.y

            if self.__orient == 0:
                start_x += i
            elif self.__orient == 1:
                start_y += i

            ship_coords.append(Coord(start_x, start_y))
        return ship_coords

    #проверка попадания
    def shooten(self,shot):
        return shot in self.coords

# класс игрового поля
class BattleBoard():
    def __init__(self,hid=False,size=6):
        self.hid=hid
        self.size=size

       #счетчик пораженных кораблей
        self.count=0

       #матрица игрового поля
        self.matrix=[ ["0"]*size for i in range(size) ]

        #список кораблей на доске
        self.ships=[]

        #список занятых клеток
        self.busy=[]


    def __str__(self):
        res = "  ! 1 ! 2 ! 3 ! 4 ! 5 ! 6 !"
        for i, row in enumerate(self.matrix):
            res += f"\n{i + 1} ! " + " ! ".join(row) + " !"

        if self.hid:
            res = res.replace("■", "O")
        return res

    #метод для проверки лежит ли точка в пределах доски
    def out(self,a):
        return not ((0<=a.x<self.size) and (0<=a.y<self.size))

    # метод отмечающий пространство вокруг корабля
    def around(self,ship,verb=False): # verb-параметр для отображения точек на клетках вблизи кораблей, для выполнения условия, что расстояние между кораблями минимум 1 клетка
        around=[
            (-1,-1),(-1,0),(-1,1),
            (0,-1),(0,0),(0,1),
            (1,-1),(1,0),(1,1)
        ]
        for i in ship.coords:
            for ix,iy in around:
                current=Coord(i.x+ix, i.y+iy)
                if not (self.out(current)) and current not in self.busy: # условие, что точка у корабля не за пределами поля и эта точка не занята
                    if verb:
                        self.matrix[current.x][current.y]="."
                    self.busy.append(current)

    # метод добавления корабля
    def add_ship(self,ship):
        for d in ship.coords:
            if self.out(d) or d in self.busy:
                raise ShipWrongAccomodationEx()
        for d in ship.coords:
            self.matrix[d.x][d.y]= "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.around(ship)


    # стрельба по полю
    def shot(self,x):
        if x in self.busy:
            raise BusyCoordEx()
        if self.out(x):
            raise OutOfBoardEx()

        self.busy.append(x) # добавить точку в список занятых точек при отсутствии исключений

        # описание попадания по кораблю или мимо
        for ship in self.ships:
            if ship.shooten(x):
                ship.lives-=1
                self.matrix[x.x][x.y]="X"
                if ship.lives==0:
                    self.count+=1
                    self.around(ship,verb=True)
                    print("Корабль уничтожен!!!")
                    return True
                else:
                    print("Корабль поврежден!")
                    return True


        self.matrix[x.x][x.y]="T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy=[]

    # проверка победы одного из игроков
    def victory(self):
        return self.count==len(self.ships)


# создание общего класса Игрока
class Player():
    def __init__(self,board,enemy):
        self.board=board
        self.enemy=enemy


    def ask(self): # метод, вызываемый в дочерних классах
        raise NotImplementedError()

    def gaming(self):
        while True:
            try:
                target=self.ask()
                repeat=self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

# класс компьютер-игрок
class AI(Player):
    def ask(self):
        x=Coord(randint(0,5),randint(0,5))
        time.sleep(2)
        print(f"Компьютер ходит на:{x.x+1} {x.y+1}")
        return x

# класс пользователь-игрок
class User(Player):
    def ask(self):
        while True:
            coords=input("Ваш ход. Введите координаты:").split()

            if len(coords)!=2:
                print("Введите 2 координаты!")
                continue

            x,y=coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Неверный формат. Введите числа!")
                continue

            x,y=int(x),int(y)

            return Coord(x-1,y-1)


# описание игрового процесса
class Game():
    def __init__(self,size=6):
        self.size=size
        self.lengths=[3, 2, 2, 1, 1, 1, 1] # список с длинами кораблей
        player=self.create_board()
        computer=self.create_board()
        computer.hid=True

        self.ai=AI(computer, player)
        self.us=User(player,computer)

    # метод для расстановки кораблей на доске
    def try_board(self):
        battle_board=BattleBoard(size= self.size)
        attempts=0 # счетчик кол-ва попыток расставить корабли
        for i in self.lengths:
            while True:
                attempts+=1
                if attempts>2500: # условие остановки бесконечного цикла расстановки, если не получается
                    return None
                ship=Ship(Coord(randint(0, self.size), (randint(0, self.size))), i, randint(0,1))
                try:
                    battle_board.add_ship(ship)
                    break
                except ShipWrongAccomodationEx:
                    pass
        battle_board.begin()
        return battle_board

    # метод который все равно создаст доску, несмотря на None в случае создания в try_board
    def create_board(self):
        battle_board=None
        while battle_board is None:
            battle_board=self.try_board()
        return battle_board

    # приветствие
    def greeting(self):
        print("     -----------------------       ")
        print("          ДОБРО ПОЖАЛОВАТЬ         ")
        print("               В ИГРУ              ")
        print('           "МОРСКОЙ БОЙ"           ')
        print("     -----------------------       ")
        print("        Необходимо вводить         ")
        print("       2 координаты: x и y         ")
        print(" x-номер строки, y-номер столбца   ")
        print("     -----------------------       ")


    def print_boards(self):
        print("-" * 15)
        print("Доска User:")
        print(self.us.board)
        print("-" * 15)
        print("Доска Computer:")
        print(self.ai.board)


    # создание игрового цикла
    def game_cycle(self):
        num = 0 # номер хода
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("-" * 15)
                print("Ходит User!")
                repeat = self.us.gaming()
            else:
                print("-" * 15)
                print("Ходит Computer!")
                repeat = self.ai.gaming()
            if repeat: # для того, чтобы счетчик снижался на 1, если игрок делает повторный выстрел при успехе и не нарушалась очередность
                num -= 1

            if self.ai.board.victory():
                self.print_boards()
                print("-" * 15)
                print("Пользователь выиграл!")
                break

            if self.us.board.victory():
                self.print_boards()
                print("-" * 15)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greeting()
        self.game_cycle()


g=Game()
g.start()