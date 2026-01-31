import shutil
import os
import random
import sys

# Settings
terminal_size = shutil.get_terminal_size((80, 20))
width = int(terminal_size.columns // 4)
height = int(terminal_size.lines // 2)
x_offset = (terminal_size.columns - width) // 2

robot_count = terminal_size.lines // 4
obstacle_count = int(terminal_size.lines // 1.5)
teleport_charges = 3

# Asset symbols
asset_symbols = {
    "robot": "R",
    "player": "@",
    "destroyed_robot": "X",
    "wall": "#",
    "obstacle": "+",
}

# Directions (dx, dy) for 8 possible moves
directions = {
    "Q": (-1, -1),  # Up-Left
    "W": (0, -1),  # Up
    "E": (1, -1),  # Up-Right
    "A": (-1, 0),  # Left
    "D": (1, 0),  # Right
    "Z": (-1, 1),  # Down-Left
    "X": (0, 1),  # Down
    "C": (1, 1),  # Down-Right
}


def print_rules():
    rules = """
    WELCOME TO HUNGRY ROBOTS!

    RULES:
    1. You are represented by the @ symbol.
    2. Each turn, you can move one space in any 8 directions, or stay still.
    3. You can also teleport to a random location 3 times per game.
    4. Robots (R) will move towards you each turn after you.
    5. Avoid robots and obstacles (+) to survive.
    6. If a robot reaches you, you lose!
    7. Destroy robots by leading them into each other.
    8. Once 2 robots collide, they turn into destroyed robot parts (X) which are obstacles.

    GOOD LUCK!
    """
    print(rules)


def get_starting_screen(width, height):
    """
    Generates the starting game screen with walls, obstacles, robots, and player.
    Args:
        width (int): Width of the game screen.
        height (int): Height of the game screen.
    Returns:
        dict: A dictionary representing the game screen with coordinates as keys and symbols as values.
        tuple: The player's starting position (x, y).
        list: A list of robot positions [(x1, y1), (x2, y2), ...].
    """
    game_screen = {}
    robots_pos = []
    # Create empty screen
    for y in range(height):
        for x in range(width):
            game_screen[(x, y)] = " "

    # Add walls
    for x in range(width):
        game_screen[(x, 0)] = asset_symbols["wall"]
        game_screen[(x, height - 1)] = asset_symbols["wall"]

    for y in range(height):
        game_screen[(0, y)] = asset_symbols["wall"]
        game_screen[(width - 1, y)] = asset_symbols["wall"]

    # Add obstacles (they go in pairs)
    for _ in range(obstacle_count // 2):
        if random.choice([True, False]):
            x = random.randint(1, width - 3)
            y = random.randint(1, height - 2)
            game_screen[(x, y)] = asset_symbols["obstacle"]
            game_screen[(x + 1, y)] = asset_symbols["obstacle"]
        else:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 3)
            game_screen[(x, y)] = asset_symbols["obstacle"]
            game_screen[(x, y + 1)] = asset_symbols["obstacle"]

    # Add robots (with a disance of at least 3 from each other)
    for _ in range(robot_count):
        while True:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            if game_screen[(x, y)] == " ":
                too_close = False
                for dx in range(-3, 4):
                    for dy in range(-3, 4):
                        if (
                            (dx**2 + dy**2 <= 9)
                            and (0 <= x + dx < width)
                            and (0 <= y + dy < height)
                        ):
                            if game_screen[(x + dx, y + dy)] == asset_symbols["robot"]:
                                too_close = True
                if not too_close:
                    game_screen[(x, y)] = asset_symbols["robot"]
                    robots_pos.append((x, y))
                    break

    # Add player (with a distance of at least 5 from any robot)
    while True:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if game_screen[(x, y)] == " ":
            too_close = False
            for dx in range(-5, 6):
                for dy in range(-5, 6):
                    if (
                        (dx**2 + dy**2 <= 25)
                        and (0 <= x + dx < width)
                        and (0 <= y + dy < height)
                    ):
                        if game_screen[(x + dx, y + dy)] == asset_symbols["robot"]:
                            too_close = True
            if not too_close:
                player_pos = (x, y)
                game_screen[player_pos] = asset_symbols["player"]
                break

    return game_screen, player_pos, robots_pos


def display_screen(screen):
    """
    Displays the game screen centered in the terminal.
    Args:
        screen (dict): A dictionary representing the game screen with coordinates as keys and symbols as values.
    """
    offset_x = (terminal_size.columns - width) // 2

    for y in range(height):
        row = " " * offset_x
        for x in range(width):
            row += screen[(x, y)]
        print(row)


def get_possible_moves(game_screen, player_pos):
    """
    Determines possible moves for the player based on current position and game screen.
    Args:
        game_screen (dict): A dictionary representing the game screen with coordinates as keys and symbols as values.
        player_pos (tuple): The player's current position (x, y).
    Returns:
        list: A list of possible move keys (e.g., ["Q", "W", "E", ...]).
    """
    possible_moves = []

    for key, (dx, dy) in directions.items():
        new_x = player_pos[0] + dx
        new_y = player_pos[1] + dy
        if game_screen.get((new_x, new_y), asset_symbols["wall"]) == " ":
            possible_moves.append(key)

    return possible_moves


def print_controls(possible_moves):
    def show(key):
        return f"({key})" if key in possible_moves else "( )"

    print(" " * x_offset + f"{show('Q')} {show('W')} {show('E')}")
    print(" " * x_offset + f"{show('A')} {show('S')} {show('D')}")
    print(" " * x_offset + f"{show('Z')} {show('X')} {show('C')}" + "\n" * 2)


def update_player_position(game_screen, player_pos, move):
    """
    Updates the player's position on the game screen based on the chosen move
    and returns the new position.
    Args:
        game_screen (dict): A dictionary representing the game screen with coordinates as keys and symbols as values.
        player_pos (tuple): The player's current position (x, y).
        move (str): The move key chosen by the player.
    Returns:
        tuple: The player's new position (x, y).
    """
    global teleport_charges

    # Teleport
    if move == "T":
        while True:
            x = random.randint(1, width - 2)
            y = random.randint(1, height - 2)
            if game_screen[(x, y)] == " ":
                game_screen[player_pos] = " "
                player_pos = (x, y)
                game_screen[player_pos] = asset_symbols["player"]
                break
        teleport_charges -= 1
        return player_pos

    # Normal move (move is necessarily possible as checked before)
    dx, dy = directions[move]
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy

    game_screen[player_pos] = " "
    player_pos = (new_x, new_y)
    game_screen[player_pos] = asset_symbols["player"]

    return player_pos


def update_robot_positions(game_screen, robots_pos, player_pos):
    """
    Update the positions of all robots on the game screen based on the player's position.

    All robots move at once, each moving one step closer to the player, diagonally if possible.
    A robot will not move into walls or obstacles.
    If a robot reaches the player, the game ends.
    If two robots collide, they turn into destroyed robot parts.
    If a robot moves onto a destroyed robot part, it is destroyed.

    Args:
        game_screen (dict): A dictionary representing the game screen with coordinates as keys and symbols as values.
        robots_pos (list of tuple): A list of robot positions [(x1, y1), (x2, y2), ...].
        player_pos (tuple): The player's current position (x, y).

    Returns:
        list of tuple: Updated list of robot positions [(x1, y1), (x2, y2), ...].
    """

    def game_over():
        os.system("cls" if os.name == "nt" else "clear")
        display_screen(game_screen)
        print("\n" * 5)
        print(" " * x_offset + "A robot has caught you! GAME OVER!")
        input("Press Enter to exit...")
        sys.exit()

    new_robots_pos = []

    for robot_pos in robots_pos:
        # Determine move direction towards player
        dx = (player_pos[0] > robot_pos[0]) - (player_pos[0] < robot_pos[0])
        dy = (player_pos[1] > robot_pos[1]) - (player_pos[1] < robot_pos[1])
        new_x = robot_pos[0] + dx
        new_y = robot_pos[1] + dy

        # Check for collision with walls or obstacles
        while True:
            if game_screen.get((new_x, new_y), asset_symbols["wall"]) in [
                asset_symbols["wall"],
                asset_symbols["obstacle"],
            ]:
                # Try to adjust move
                if dx != 0 and dy != 0:
                    # Try horizontal move only
                    if (
                        game_screen.get(
                            (robot_pos[0] + dx, robot_pos[1]), asset_symbols["wall"]
                        )
                        == " "
                    ):
                        new_x = robot_pos[0] + dx
                        new_y = robot_pos[1]
                        break
                    # Try vertical move only
                    elif (
                        game_screen.get(
                            (robot_pos[0], robot_pos[1] + dy), asset_symbols["wall"]
                        )
                        == " "
                    ):
                        new_x = robot_pos[0]
                        new_y = robot_pos[1] + dy
                        break
                    else:
                        # Can't move
                        new_x = robot_pos[0]
                        new_y = robot_pos[1]
                        break
                elif dx != 0:
                    # Try vertical moves
                    if (
                        game_screen.get(
                            (robot_pos[0], robot_pos[1] + 1), asset_symbols["wall"]
                        )
                        == " "
                    ):
                        new_x = robot_pos[0]
                        new_y = robot_pos[1] + 1
                        break
                    elif (
                        game_screen.get(
                            (robot_pos[0], robot_pos[1] - 1), asset_symbols["wall"]
                        )
                        == " "
                    ):
                        new_x = robot_pos[0]
                        new_y = robot_pos[1] - 1
                        break
                    else:
                        # Can't move
                        new_x = robot_pos[0]
                        new_y = robot_pos[1]
                        break
                elif dy != 0:
                    # Try horizontal moves
                    if (
                        game_screen.get(
                            (robot_pos[0] + 1, robot_pos[1]), asset_symbols["wall"]
                        )
                        == " "
                    ):
                        new_x = robot_pos[0] + 1
                        new_y = robot_pos[1]
                        break
                    elif (
                        game_screen.get(
                            (robot_pos[0] - 1, robot_pos[1]), asset_symbols["wall"]
                        )
                        == " "
                    ):
                        new_x = robot_pos[0] - 1
                        new_y = robot_pos[1]
                        break
                    else:
                        # Can't move
                        new_x = robot_pos[0]
                        new_y = robot_pos[1]
                        break
                else:
                    # Can't move
                    new_x = robot_pos[0]
                    new_y = robot_pos[1]
                    break

        # Check for collision with player
        if (new_x, new_y) == player_pos:
            game_over()

        # Check for collision with other robots
        if (new_x, new_y) in new_robots_pos:
            # Destroy both robots
            game_screen[(new_x, new_y)] = asset_symbols["destroyed_robot"]
            new_robots_pos.remove((new_x, new_y))
            continue

        # Check for collision with destroyed robot parts
        if game_screen.get((new_x, new_y)) == asset_symbols["destroyed_robot"]:
            # Robot is destroyed
            game_screen[robot_pos] = " "
            robots_pos.remove(robot_pos)
            continue

        # Add robot
        new_robots_pos.append((new_x, new_y))

    # Update game screen at once after all moves
    for robot_pos in robots_pos:
        if game_screen.get(robot_pos) == asset_symbols["robot"]:
            game_screen[robot_pos] = " "
    for robot_pos in new_robots_pos:
        game_screen[robot_pos] = asset_symbols["robot"]

    return new_robots_pos


def main():
    print_rules()
    input("Press Enter to start the game...")
    game_screen, player_pos, robots_pos = get_starting_screen(width, height)

    while True:
        possible_moves = get_possible_moves(game_screen, player_pos)

        # Clear screen and display
        os.system("cls" if os.name == "nt" else "clear")
        display_screen(game_screen)

        # Print controls
        print("\n" * 5)
        print(
            " " * x_offset + f"(T)eleport charges left: {teleport_charges}" + "\n" * 2
        )
        print_controls(possible_moves)

        # Get player move
        while True:
            move = input("Enter your move (or Quit): ").upper()
            if (
                move in possible_moves
                or (move == "T" and teleport_charges > 0)
                or move == "QUIT"
            ):
                break
            # No teleport charges left
            elif move == "T" and teleport_charges == 0:
                print("No teleport charges left. Please choose another move.")
            # Invalid move
            else:
                print("Invalid move. Please try again.")

        # Check for quit
        if move == "QUIT":
            break

        # Update positions
        if move != "S":
            player_pos = update_player_position(game_screen, player_pos, move)
        robots_pos = update_robot_positions(game_screen, robots_pos, player_pos)

    print("Thanks for playing!")
    sys.exit()


if __name__ == "__main__":
    main()

# add quit option
# J'ai bien fait de traiter le "S" separement ?
# global teleport_charges -- Necessary ?
# Verif collision avec robots consid dans possible moves ?
# La def game_over() est-elle bien placée ?
