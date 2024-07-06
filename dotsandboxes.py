import copy
import math
import random
import time

class DotsAndBoxes:
    def __init__(self, rows, columns):
        self.play_dict = {}
        for i in range(rows):
            for j in range(columns - 1):
                self.play_dict[((j + (i * columns)), j + (i * columns) + 1)] = 0

        for i in range(rows - 1):
            for j in range(columns):
                self.play_dict[(j + (i * columns), j + columns + (i * columns))] = 0

        self.score_dict = {}
        for i in range(rows - 1):
            for j in range(columns - 1):
                box = [(j + i * columns, j + i * columns + 1)]
                box.append((box[0][0], box[0][1] + columns - 1))
                box.append((box[0][0] + 1, box[0][1] + columns))
                box.append((box[0][0] + columns, box[2][1]))
                self.score_dict[tuple(box)] = 0

        self.row_count = rows
        self.column_count = columns

        self.a_score = 0
        self.b_score = 0

    def get_row(self, i):
        left = (i * self.column_count)
        right = left + 1
        for j in range(self.column_count - 1):
            if self.play_dict[(left, right)] == 0:
                print("{:^3d}".format(left), end="   ")
            else:
                print("{:^3d} -".format(left), end=" ")
            left = right
            right = left + 1
        print("{:^3d}".format(left))

    def get_vertical(self, upper_left, upper_right):
        if self.play_dict[(upper_left, upper_right)] == 0:
            print("  ", end=" ")
        else:
            print(" |", end=" ")

    def get_middle_row(self, i):
        upper_left = (i * self.column_count)
        upper_right = upper_left + 1
        bottom_left = upper_left + self.column_count
        bottom_right = bottom_left + 1

        for j in range(self.column_count - 1):
            self.get_vertical(upper_left, bottom_left)

            top = (upper_left, upper_right)
            left = (upper_left, bottom_left)
            right = (upper_right, bottom_right)
            bottom = (bottom_left, bottom_right)
            score = self.score_dict[(top, left, right, bottom)]

            if score == 0:
                print("  ", end=" ")
            else:
                print(" " + score, end=" ")

            upper_left, bottom_left = upper_right, bottom_right
            upper_right += 1
            bottom_right += 1
        self.get_vertical(upper_left, bottom_left)
        print()

    def get(self):
        for i in range(self.row_count - 1):
            self.get_row(i)
            self.get_middle_row(i)

        self.get_row(self.row_count - 1)
        print("\nPlayer A: {} Player B: {}".format(self.a_score, self.b_score))

    def check_for_scores(self, player_a):
        player = "A" if player_a else "B"
        taken_set = {i for i in self.play_dict if self.play_dict[i] == 1}
        open_scores = [i for i in self.score_dict if self.score_dict[i] == 0]

        score_counter = 0

        for box in open_scores:
            if set(box).issubset(taken_set):
                score_counter += 1
                self.score_dict[box] = player
        return score_counter

    def make_play(self, start_point, end_point, player_a):
        try:
            if self.play_dict[(start_point, end_point)] == 1:
                return False
        except KeyError:
            return False

        self.play_dict[(start_point, end_point)] = 1
        score = self.check_for_scores(player_a)
        if player_a:
            self.a_score += score
        else:
            self.b_score += score
        return True

    def get_open_plays(self):
        return [i for i in self.play_dict if self.play_dict[i] == 0]

    def isover(self):
        return self.a_score + self.b_score == len(self.score_dict)

class HumanPlayer:
    def __init__(self, player_a):
        self.player_a = player_a
        self.playername = "A" if player_a else "B"

    def make_play(self, game):
        while True:
            move = input("Player {}, make your move (start point end point): ".format(self.playername))
            move = move.split()
            try:
                move[0], move[1] = int(move[0]), int(move[1])
                if len(move) != 2:
                    print("Error. Input must be of form start point, endpoint")
                    continue
            except ValueError:
                print("Error. Input must be integers")
                continue
            move.sort()
            valid_move = game.make_play(*move, self.player_a)
            if valid_move:
                return ()
            print("Error. That move does not exist. Try again")

class MinimaxPlayer:
    def __init__(self, player_a):
        self.player = player_a

    def minimax(self, game, player_a, depth):
        if depth == 0 or game.isover():
            return game.a_score - game.b_score

        if player_a:
            value = -math.inf
            for move in game.get_open_plays():
                new_game = copy.deepcopy(game)
                new_game.make_play(*move, True)
                value = max(value, self.minimax(new_game, False, depth - 1))
            return value
        else:
            value = math.inf
            for move in game.get_open_plays():
                new_game = copy.deepcopy(game)
                new_game.make_play(*move, False)
                value = min(value, self.minimax(new_game, True, depth - 1))
            return value

    def make_play(self, game):
        start_time = time.time()

        play_space_size = len(game.get_open_plays())
        if play_space_size == 1:
            play = random.choice(game.get_open_plays())
            game.make_play(*play, self.player)
            return

        depth = math.floor(math.log(19000, play_space_size))

        best_score = -math.inf
        best_play = None
        for move in game.get_open_plays():
            new_game = copy.deepcopy(game)
            new_game.make_play(*move, self.player)
            score = self.minimax(new_game, False, depth)
            if score > best_score:
                best_score = score
                best_play = move

        elapsed = time.time() - start_time

        if best_play is None:
            best_play = random.choice(game.get_open_plays())
        game.make_play(*best_play, self.player)

        player = "A" if self.player else "B"
        print("Player {}'s move: {} {}".format(player, *best_play))
        print("Time elapsed to make move: {}".format(elapsed))

class Game:
    def __init__(self, player_a_type="human", player_b_type="minimax", rows=5, columns=5):
        self.rows = rows
        self.columns = columns

        if player_a_type == "human":
            self.player_a = HumanPlayer(True)
        elif player_a_type == "minimax":
            self.player_a = MinimaxPlayer(True)

        if player_b_type == "random":
            self.player_b = RandomPlayer(False)
        elif player_b_type == "minimax":
            self.player_b = MinimaxPlayer(False)
        else:
            self.player_b = HumanPlayer(False)

    def play_game(self):
        game = DotsAndBoxes(self.rows, self.columns)

        print()
        game.get()
        print()

        coin_toss = random.randint(1, 2)
        print("The coin landed on {}".format("heads" if coin_toss == 1 else "tails"))
        print("Player {} goes first".format("A" if coin_toss == 1 else "B"))
        print()

        while not game.isover():
            while not game.isover():
                if coin_toss == 2:
                    coin_toss = 3
                    break
                old_score = game.a_score
                self.player_a.make_play(game)
                game.get()
                if old_score == game.a_score:
                    break

            while not game.isover():
                old_score = game.b_score
                self.player_b.make_play(game)
                game.get()
                if old_score == game.b_score:
                    break

        if game.a_score == game.b_score:
            print("It's a tie!")
        elif game.a_score >= game.b_score:
            print("You wins!")
        else:
            print("AgentAI wins!")

def main():
    print("Welcome to Make Squares Game!")
    
    wanna_play_again = "yes"
    while wanna_play_again == "yes":
        while True:
            rows = input("How many rows should the grid have? (Do not exceed 32 rows): ")
            try:
                rows = int(rows)
                if rows > 32:
                    print("Too many rows! Please try again (Do not exceed 32 rows)")
                    continue
            except ValueError:
                print("Not an integer. Please try again.")
                continue
            break

        while True:
            limit = math.floor(min(16, 9999 / rows))
            columns = input("How many columns should the grid have? (limit {}): ".format(limit))
            try:
                columns = int(columns)
                if columns > limit:
                    print("Too many columns! Try again (limit {})".format(limit))
                    continue
            except ValueError:
                print("That is not an integer value! try again")
                continue
            break

        game_play = Game("human", "minimax", rows, columns)
        game_play.play_game()

        wanna_play_again = input("Play again? (y/n): ")

    print("Thank you for playing!")

if __name__ == "__main__":
    main()
