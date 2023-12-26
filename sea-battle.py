import random as rnd
MARK_UNKNOWN = 'O'
MARK_SHIP = '■'
MARK_MISS = 'T'
MARK_HIT = 'X'
SHIPS = [(3, 1,), (2, 2), (1, 4)]
SIDES = [(-1, 0), (1, 0), (0, -1), (0, 1)]
WINNER = None


class Player:
    def __init__(self, board, visible_enemy_board):
        self.board = board
        self.visible_enemy_board = visible_enemy_board

    def getPlayerBoard(self):
        return self.board

    def setPlayerBoard(self, x, y, mark):
        self.board[x][y] = mark

    def getVisibleBoard(self):
        return self.visible_enemy_board

    def setVisibleBoard(self, x, y, mark):
        self.visible_enemy_board[x][y] = mark


class AI:
    def __init__(self, board):
        self.AIboard = self.takeBoard(board)
    def getAIBoard(self):
        return self.AIboard

    def setAIBoard(self, x, y, mark):
        self.AIboard[x][y] = mark

    def takeBoard(self, board):
        self.AIboard = board


class Boards(Player, AI):
    def __init__(self, p):
        self.p = p
        super().__init__(self.getBoard(True), self.__getClearBoard())
        AI.takeBoard(self, self.getBoard(False))

    def getBoard(self, player):
        board = self.__getClearBoard()
        for deck, ship_size in SHIPS:
            for i in range(ship_size):
                while True:
                    if not player:
                        x = rnd.randint(1, self.p)
                        y = rnd.randint(1, self.p)
                        side = rnd.choice(SIDES)
                    if player:
                        self.printBoard(board)
                        print(f'Введите координаты для {deck}-палубного корабля')
                        ship_input = self.inputCoordinates()
                        x = ship_input[0]
                        y = ship_input[1]
                        if deck != 1:
                            side = SIDES[self.__inputSide()]
                    try:
                        if self.__canEnterShip(x, y, board, side, deck):
                            self.__placeShip(x, y, board, deck, side)
                            break
                    except ZeroDivisionError:
                        if player:
                            print('Отсутствует расстояние между кораблями')
                    except MemoryError:
                        if player:
                            print('Корабль не может выходить за пределы поля')
                    except PermissionError:
                        if player:
                            print('Корабли не должны соприкасаться')

        return board

    def __getClearBoard(self) -> list:
        clear_board = [[MARK_UNKNOWN for _ in range(self.p)] for _ in range(self.p)]
        for i in range(self.p):
            if i != 0:
                clear_board[0][i] = str(i)
                clear_board[i][0] = str(i)
        clear_board[0][0] = ' '
        return clear_board

    def __canEnterShip(self, x, y, board, side, size):
        for i in range(size):
            if not (1 <= x <= 6 and 1 <= y <= 6 and board[x][y] != MARK_SHIP):
                raise MemoryError()
            elif not (board[x][y] != MARK_SHIP):
                raise PermissionError()
            for xx, yy in SIDES:
                try:
                    if not (board[x + xx][y] != MARK_SHIP):
                        raise ZeroDivisionError()
                except IndexError:
                    pass
                try:
                    if not (board[x][y + yy] != MARK_SHIP):
                        raise ZeroDivisionError()
                except IndexError:
                    pass
            x += side[0]
            y += side[1]
        return True

    def inputCoordinates(self):
        try:
            x = int(input('Введите номер строки: '))
            y = int(input('Введите номер столбца: '))
            if not (1 <= x <= 6 and 1 <= y <= 6):
                raise ValueError()
        except ValueError:
            print('Введите номера строк и столбцов цифрами от 1 до 6')
            return self.inputCoordinates()
        else:
            return x, y


    def __inputSide(self, first=True):
        if first == True:
            print('Введите сторону в которую вы хотите продолжить корабль '
                  '(нужно что бы между кораблями была хотя бы одна свободная клетка): ')
            print('1.Вверх')
            print('2.Вниз')
            print('3.Влево')
            print('4.Вправо')
        try:
            side = int(input("Ввод: "))
            if not (1 <= side <= 4):
                raise ValueError()
        except ValueError:
            print('Введите ответ от 1 до 4')
            return self.__inputSide(first=False)
        return side - 1

    def __placeShip(self, x, y, board, size, side):
        for i in range(size):
            board[x][y] = MARK_SHIP
            x += side[0]
            y += side[1]

    @staticmethod
    def printBoard(board):
        print(*[' | '.join(row) for row in board], sep='\n')
        print()

    def CheckWin(self, board) -> bool:
        _ship = 0
        for row in board:
            if MARK_SHIP in row:
                _ship += 1
        if _ship == 0:
            return True
        return False



class Game(Boards):
    def __init__(self, p=6):
        super().__init__(p + 1)

    def start(self):
        round = 0
        winner = 0
        while True:
            print('\n', '-------------------------------', '\n')
            print('Ваша доска')
            self.printBoard((self.getPlayerBoard()))
            print('-------------------------------', '\n')
            print('Видимая доска противника')
            self.printBoard(self.getVisibleBoard())
            print('-------------------------------', '\n')
            winner = 1
            self.PlayerHit()
            if self.CheckWin(self.getAIBoard()):
                raise TimeoutError()
            winner = 2
            self.AIHit()
            if self.CheckWin(self.getPlayerBoard()):
                raise NameError()
            round += 1
            print(f'Раунд {round} завершен')
            cmd = input("Нажмите любую кнопку что бы продолжить или X что бы выйти: ")
            if cmd == 'X':
                raise KeyboardInterrupt()

    def PlayerHit(self):
        print('Введите координаты для выстрела')
        _visibleBoard = self.getVisibleBoard()
        _enemyBoard = self.getAIBoard()
        while True:
            try:
                _x = int(input('Введите номер строки: '))
                _y = int(input('Введите номер столбца: '))
                if not (1 <= _x <= 6 and 1 <= _y <= 6):
                    raise ValueError()
                self.CheckHit(_visibleBoard, _x, _y)
            except ZeroDivisionError:
                print('Вы уже стреляли в эту точку')

            except ValueError:
                print('Введите числа от 1 до 6')
            else:
                break
        if _enemyBoard[_x][_y] == MARK_SHIP:

            self.setAIBoard(_x, _y, MARK_HIT)
            self.setVisibleBoard(_x, _y, MARK_HIT)
            print('\n', '-------------------------------', '\n')
            self.printBoard(self.getVisibleBoard())
            print('Попадание!')
            print('\n', '-------------------------------', '\n')

        else:
            self.setAIBoard(_x, _y, MARK_MISS)
            self.setVisibleBoard(_x, _y, MARK_MISS)
            print('\n', '-------------------------------', '\n')
            self.printBoard(self.getVisibleBoard())
            print('Промах!')
            print('\n', '-------------------------------', '\n')


    def AIHit(self):
        _enemyBoard = self.getPlayerBoard()
        while True:
            try:
                _x = rnd.randint(1, 6)
                _y = rnd.randint(1, 6)
                self.CheckHit(_enemyBoard, _x, _y)
            except ZeroDivisionError:
                pass
            else:
                break
        print(f'Бот стрельнул в {_x} {_y}')
        if _enemyBoard[_x][_y] == MARK_SHIP:
            self.setPlayerBoard(_x, _y, MARK_HIT)
            print('\n', '-------------------------------', '\n')
            self.printBoard(self.getPlayerBoard())
            print('Попадание!')
            print('\n', '-------------------------------', '\n')
        else:
            self.setPlayerBoard(_x, _y, MARK_MISS)
            print('\n', '-------------------------------', '\n')
            self.printBoard(self.getPlayerBoard())
            print('Промах!')
            print('\n', '-------------------------------', '\n')


    @staticmethod
    def CheckHit(board, x, y):
        if board[x][y] in (MARK_MISS, MARK_HIT):
            raise ZeroDivisionError()


if __name__ == "__main__":
    try:
        game = Game(6)
        print(game.start())
    except TimeoutError:
        print('Вы выйграли!')
    except NameError:
        print('Вы проиграли!')
    except KeyboardInterrupt:
        print('\n', 'Игра закончена, удачи)')