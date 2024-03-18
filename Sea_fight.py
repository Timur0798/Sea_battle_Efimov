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

class WrongCoordEx(BoardException):
    def __str__(self):
        print("В эту точку уже стреляли")

# неверное размещение корабля
class BoardWrongAccomodationEx(BoardException):
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
        self.matrix=[ [0]*size for i in range(size) ]

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

b=BattleBoard()
print(b)