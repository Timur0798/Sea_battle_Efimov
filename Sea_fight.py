#создание класса точки-координаты выстрела
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
        print("Выстрел за пределы поля")

class BusyCoordEx(BoardException):
    def __str__(self):
        print("В эту точку уже стреляли")

# неверное размещение корабля
class ShipWrongAccomodationEx(BoardException):
    pass

# создание класса корабля
class Ship():
    def __init__(self,bow,len,orient):
        self.bow=bow
        self.len=len
        self.orient=orient
        self.lives = len

    # метод для размещения корабля горизотально или вертикально
    @property
    def coords(self):
        ship_coords=[]
        for i in range(self.len):
            start_x=self.bow.x
            start_y=self.bow.y

            if self.orient == 0:
                start_x += i
            elif self.orient == 1:
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
                    return False
                else:
                    print("Корабль поврежден!")
                    return True

        self.matrix[x.x][x.y]="."
        print("Мимо!")
        return False

    def begin(self):
        self.busy=[]

# создание класса Игрока
class Player():
    def __init__(self,board,enemy):
        self.board=board
        self.enemy=enemy