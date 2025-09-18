import math
import random

# === Constants ===

WIN_LINES = [
    [(0,0),(0,1),(0,2)],  # rows
    [(1,0),(1,1),(1,2)],
    [(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0)],  # cols
    [(0,1),(1,1),(2,1)],
    [(0,2),(1,2),(2,2)],
    [(0,0),(1,1),(2,2)],  # diagonals
    [(0,2),(1,1),(2,0)]
]

# === Game Board Class ===

class GameBoard:
    def __init__(self):
        self.entries = [[0, 0, 0], [0, 0, 0], [0, 0 ,0]]

    def print_board(self):
        symbols = {0: " ", 1: "X", 2: "O"}
        print("\nCurrent Board:")
        for row in self.entries:
            print(" | ".join(symbols[cell] for cell in row))
            print("-" * 9)

    def checkwin(self) -> int:
        for line in WIN_LINES:
            vals = [self.entries[r][c] for r,c in line]
            if vals == [1, 1, 1]:
                return 1
            if vals == [2, 2, 2]:
                return 2
        if any(0 in row for row in self.entries):
            return 0  # game ongoing
        return 3  # draw

    def check_nextplayer(self, bd=None):
        if bd is None:
            bd = self.entries
        count_1 = sum(cc == 1 for row in bd for cc in row)
        count_2 = sum(cc == 2 for row in bd for cc in row)
        return 1 if count_1 == count_2 else 2

    def get_moves(self):
        return [(r,c) for r in range(3) for c in range(3) if self.entries[r][c]==0]

    def copy(self):
        new_board = GameBoard()
        new_board.entries = [row[:] for row in self.entries]
        return new_board

# === MCTS Node and Agent ===

class MCTSNode:
    def __init__(self, bd: GameBoard, parent=None, action=None):
        self.bd = bd
        self.parent = parent
        self.action = action
        self.children = []
        self.possible_moves = bd.get_moves()
        self.visits = 0
        self.wins = 0.0

    def is_fully_expanded(self):
        return len(self.possible_moves) == 0

    def is_terminal(self):
        return self.bd.checkwin() != 0

def apply_action(bd: GameBoard, action, player):
    r, c = action
    new_bd = bd.copy()
    new_bd.entries[r][c] = player
    return new_bd

class MCTS:
    def __init__(self, c=math.sqrt(2)):
        self.c = c

    def uct_select(self, node: MCTSNode):
        return max(
            node.children,
            key=lambda child: (child.wins / child.visits) + self.c * math.sqrt(math.log(node.visits) / child.visits)
        )

    def expand(self, node: MCTSNode):
        action = node.possible_moves.pop()
        player = node.bd.check_nextplayer(node.bd.entries)
        child_bd = apply_action(node.bd, action, player)
        child_node = MCTSNode(child_bd, parent=node, action=action)
        node.children.append(child_node)
        return child_node

    def rollout(self, bd: GameBoard):
        rollout_bd = bd.copy()
        while rollout_bd.checkwin() == 0:
            player = rollout_bd.check_nextplayer(rollout_bd.entries)
            moves = rollout_bd.get_moves()
            if not moves:
                break
            action = random.choice(moves)
            rollout_bd.entries[action[0]][action[1]] = player
        winner = rollout_bd.checkwin()
        return +1 if winner == 1 else -1 if winner == 2 else 0

    def backpropagate(self, node: MCTSNode, reward: int):
        current = node
        while current is not None:
            current.visits += 1
            current.wins += reward
            reward = -reward
            current = current.parent

    def search(self, root: MCTSNode, iterations=1000):
        for _ in range(iterations):
            node = root

            # Selection
            while not node.is_terminal() and node.is_fully_expanded():
                node = self.uct_select(node)

            # Expansion
            if not node.is_terminal() and not node.is_fully_expanded():
                node = self.expand(node)

            # Simulation
            reward = self.rollout(node.bd)

            # Backpropagation
            self.backpropagate(node, reward)

        # Choose best child (no exploration)
        return max(root.children, key=lambda c: c.visits).action


def MCTS_move(state: GameBoard, iterations=1000):
    mcts = MCTS()
    root = MCTSNode(state)
    best_action = mcts.search(root, iterations=iterations)
    player = state.check_nextplayer()
    next_state = apply_action(state, best_action, player)
    return best_action, next_state

# === Input Validation ===

def get_valid_input(board: GameBoard):
    while True:
        try:
            user_input = input("Enter your move (0–8): ").strip()
            index = int(user_input)
            if index < 0 or index > 8:
                print("Input must be between 0 and 8.")
                continue
            r, c = divmod(index, 3)
            if board.entries[r][c] != 0:
                print("That space is already taken.")
                continue
            return r, c
        except ValueError:
            print("Invalid input. Please enter a number from 0 to 8.")

# === Main Game Loop ===

def play_game():
    print("Welcome to Tic Tac Toe with MCTS!")
    print("Board index layout:")
    print("0 | 1 | 2\n3 | 4 | 5\n6 | 7 | 8")

    # Symbol assignment
    symbol = ""
    while symbol not in ['X', 'O']:
        symbol = input("Do you want to be X or O? ").strip().upper()

    player_symbol = 1 if symbol == 'X' else 2
    ai_symbol = 2 if player_symbol == 1 else 1

    try:
        iterations = int(input("Enter number of MCTS simulations (e.g. 1000): "))
    except ValueError:
        iterations = 1000
        print("Invalid number. Using default 1000 iterations.")

    board = GameBoard()

    while board.checkwin() == 0:
        board.print_board()
        current_player = board.check_nextplayer()

        if current_player == player_symbol:
            print("Your move.")
            move = get_valid_input(board)
            board.entries[move[0]][move[1]] = player_symbol
        else:
            print("MCTS is thinking...")
            move, board = MCTS_move(board, iterations=iterations)
            print(f"MCTS plays at position {move[0] * 3 + move[1]}")

    # Game over
    board.print_board()
    result = board.checkwin()
    if result == player_symbol:
        print("🎉 You win!")
    elif result == ai_symbol:
        print("🤖 MCTS wins!")
    else:
        print("🤝 It's a draw!")

# === Run the Game ===

if __name__ == "__main__":
    play_game()