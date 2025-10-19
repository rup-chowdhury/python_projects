import heapq
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum
import turtle
import time

class Direction(Enum):
    NORTH = 0
    EAST = 1  
    SOUTH = 2
    WEST = 3

class MazeNode:
    def __init__(self, position, direction, g_cost=0, h_cost=0, parent=None):
        self.position = position  # (row, col)
        self.direction = direction  # Direction enum
        self.g_cost = g_cost  # Cost from start
        self.h_cost = h_cost  # Heuristic cost to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent

    def __lt__(self, other):
        return self.f_cost < other.f_cost

    def __eq__(self, other):
        return self.position == other.position and self.direction == other.direction

    def __hash__(self):
        return hash((self.position, self.direction))

class MazeSolver:
    def __init__(self, maze):
        self.maze = np.array(maze)
        self.rows, self.cols = self.maze.shape

        # Direction vectors: North, East, South, West
        self.direction_vectors = {
            Direction.NORTH: (-1, 0),
            Direction.EAST: (0, 1),
            Direction.SOUTH: (1, 0),
            Direction.WEST: (0, -1)
        }

        # Start from bottom right corner as specified
        self.start_pos = (0, 7)
        # End at top left corner (can be modified as needed)
        self.end_pos = (6, 0)

        print(f"Start position: {self.start_pos}")
        print(f"End position: {self.end_pos}")

    def is_valid_position(self, position):
        """Check if position is within bounds and walkable"""
        row, col = position
        return (0 <= row < self.rows and 
                0 <= col < self.cols and 
                self.maze[row, col] == 0)

    def euclidean_distance(self, pos1, pos2):
        """Heuristic function - Euclidean distance"""
        return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def get_possible_actions(self, current_node):
        """Get all possible actions based on movement constraints"""
        actions = []

        # Action 1: Move Forward
        forward_vector = self.direction_vectors[current_node.direction]
        new_pos = (current_node.position[0] + forward_vector[0], 
                   current_node.position[1] + forward_vector[1])

        if self.is_valid_position(new_pos):
            actions.append(('forward', new_pos, current_node.direction))

        # Action 2: Turn Right and Move Forward
        right_direction = Direction((current_node.direction.value + 1) % 4)
        right_vector = self.direction_vectors[right_direction]
        right_pos = (current_node.position[0] + right_vector[0],
                     current_node.position[1] + right_vector[1])

        if self.is_valid_position(right_pos):
            actions.append(('turn_right', right_pos, right_direction))

        # Action 3: Turn Left and Move Forward
        left_direction = Direction((current_node.direction.value - 1) % 4)
        left_vector = self.direction_vectors[left_direction]
        left_pos = (current_node.position[0] + left_vector[0],
                    current_node.position[1] + left_vector[1])

        if self.is_valid_position(left_pos):
            actions.append(('turn_left', left_pos, left_direction))

        return actions

    def solve(self):
        """Solve maze using A* algorithm with movement constraints"""
        # Initialize with agent facing North
        start_node = MazeNode(
            position=self.start_pos,
            direction=Direction.NORTH,
            g_cost=0,
            h_cost=self.euclidean_distance(self.start_pos, self.end_pos)
        )

        open_list = [start_node]
        closed_set = set()

        step_count = 0

        print("\nStarting A* maze solving with movement constraints...")
        print(f"Initial state: Position {start_node.position}, Direction {start_node.direction.name}")

        while open_list:
            # Get node with lowest f_cost
            current_node = heapq.heappop(open_list)

            # Add to closed set
            closed_set.add(current_node)

            step_count += 1
            if step_count <= 20 or step_count % 50 == 0:
                print(f"Step {step_count}: Exploring position {current_node.position}, "
                      f"direction {current_node.direction.name}, f_cost: {current_node.f_cost:.2f}")

            # Check if we reached the goal
            if current_node.position == self.end_pos:
                print(f"\n*** GOAL REACHED in {step_count} exploration steps! ***")
                return self.reconstruct_path(current_node)

            # Explore possible actions
            possible_actions = self.get_possible_actions(current_node)

            for action_type, new_position, new_direction in possible_actions:
                new_node = MazeNode(
                    position=new_position,
                    direction=new_direction,
                    parent=current_node
                )

                # Skip if already in closed set
                if new_node in closed_set:
                    continue

                # Calculate costs (different costs for different actions)
                if action_type == 'forward':
                    move_cost = 1.0
                else:  # turning has slightly higher cost
                    move_cost = 1.1

                new_g_cost = current_node.g_cost + move_cost
                new_h_cost = self.euclidean_distance(new_position, self.end_pos)

                new_node.g_cost = new_g_cost
                new_node.h_cost = new_h_cost
                new_node.f_cost = new_g_cost + new_h_cost

                # Check if this path to the node is better
                existing_node = None
                for node in open_list:
                    if node == new_node:
                        existing_node = node
                        break

                if existing_node is None:
                    heapq.heappush(open_list, new_node)
                elif new_g_cost < existing_node.g_cost:
                    existing_node.g_cost = new_g_cost
                    existing_node.f_cost = new_g_cost + existing_node.h_cost
                    existing_node.parent = current_node

        print("No path found!")
        return None

    def reconstruct_path(self, goal_node):
        """Reconstruct path from goal to start"""
        path = []
        current = goal_node

        while current is not None:
            path.append((current.position, current.direction))
            current = current.parent

        path.reverse()
        return path

    def print_solution_steps(self, path):
        """Print detailed solution steps"""
        if not path:
            print("No solution to display!")
            return

        print(f"\n=== SOLUTION PATH ({len(path)} steps) ===")
        for i, (position, direction) in enumerate(path):
            action = ""
            if i > 0:
                prev_dir = path[i-1][1]
                if direction == prev_dir:
                    action = " -> Move Forward"
                elif direction == Direction((prev_dir.value + 1) % 4):
                    action = " -> Turn Right & Move"
                elif direction == Direction((prev_dir.value - 1) % 4):
                    action = " -> Turn Left & Move"
                else:
                    action = " -> Turn Around & Move"

            print(f"Step {i+1:2d}: Position {position}, Facing {direction.name:5s}{action}")

    def visualize_solution(self, path):
        """Create visual representation of maze and solution path"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))

        # Create maze visualization
        maze_display = np.copy(self.maze).astype(float)

        # Color mapping: 0 = white (walkable), 1 = black (wall)
        ax.imshow(maze_display, cmap='gray_r', interpolation='nearest')

        if path:
            # Extract positions from path
            path_positions = [pos for pos, direction in path]

            # Plot path in red
            path_y = [pos[0] for pos in path_positions]
            path_x = [pos[1] for pos in path_positions]
            ax.plot(path_x, path_y, 'r-', linewidth=4, alpha=0.8, label='Solution Path')

            # Mark start point in green
            ax.plot(self.start_pos[1], self.start_pos[0], 'go', markersize=15, label='Start', markeredgecolor='black', markeredgewidth=2)

            # Mark end point in blue
            ax.plot(self.end_pos[1], self.end_pos[0], 'bo', markersize=15, label='End', markeredgecolor='black', markeredgewidth=2)

            # Add direction arrows at key points
            arrow_points = path[::max(1, len(path)//8)]  # Show ~8 arrows along path
            for pos, direction in arrow_points:
                dx, dy = self.direction_vectors[direction]
                ax.arrow(pos[1], pos[0], dy*0.3, dx*0.3, 
                        head_width=0.15, head_length=0.15, fc='orange', ec='darkorange', alpha=0.7, linewidth=2)

        ax.set_title('A* Maze Solver with Movement Constraints\n'
                    f'Path: {len(path)} steps from {self.start_pos} to {self.end_pos}', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        # Set axis labels
        ax.set_xlabel('Column', fontsize=12)
        ax.set_ylabel('Row', fontsize=12)

        # Invert y-axis to match matrix representation
        ax.invert_yaxis()

        plt.tight_layout()
        plt.savefig('maze_solution.png', dpi=300, bbox_inches='tight')
        plt.show()

        return fig

    def visualize_with_turtle(self, path, cell_size=40, delay=0.15):
        """Visualize the maze and path using the turtle module.

        Draws the grid (walls and free cells), then animates the agent following
        the solution path with orientation arrows.
        """
        try:
            rows, cols = self.rows, self.cols

            # Setup screen
            screen = turtle.Screen()
            screen.title('A* Maze Solver - Turtle Visualization')

            width = cols * cell_size
            height = rows * cell_size

            screen.setup(width=width + 80, height=height + 80)

            origin_x = - (cols * cell_size) / 2
            origin_y = (rows * cell_size) / 2

            drawer = turtle.Turtle()
            drawer.hideturtle()
            drawer.speed('fastest')
            drawer.penup()

            def cell_top_left(r, c):
                x = origin_x + c * cell_size
                y = origin_y - r * cell_size
                return x, y

            # Draw grid cells
            for r in range(rows):
                for c in range(cols):
                    x, y = cell_top_left(r, c)
                    drawer.goto(x, y)
                    drawer.setheading(0)
                    drawer.pendown()
                    # Fill walls as black, free cells as white
                    if self.maze[r, c] == 1:
                        drawer.fillcolor('black')
                    else:
                        drawer.fillcolor('white')
                    drawer.begin_fill()
                    for _ in range(4):
                        drawer.forward(cell_size)
                        drawer.right(90)
                    drawer.end_fill()
                    drawer.penup()

            # Create agent turtle
            agent = turtle.Turtle()
            agent.shape('triangle')
            agent.color('red')
            agent.penup()
            agent.speed(1)

            def cell_center(r, c):
                x, y = cell_top_left(r, c)
                return x + cell_size / 2, y - cell_size / 2

            # Mark start and end
            sx, sy = cell_center(*self.start_pos)
            ex, ey = cell_center(*self.end_pos)

            marker = turtle.Turtle()
            marker.hideturtle()
            marker.penup()
            marker.goto(sx, sy)
            marker.dot(cell_size // 2, 'green')
            marker.goto(ex, ey)
            marker.dot(cell_size // 2, 'blue')

            # If no path, just wait
            if not path:
                screen.textinput('No path', 'No path found. Press Enter to close.')
                turtle.bye()
                return

            # Animate agent along path
            path_positions = [pos for pos, _ in path]
            centers = [cell_center(r, c) for r, c in path_positions]

            agent.goto(centers[0])
            agent.pendown()

            for i in range(1, len(centers)):
                cx, cy = centers[i]
                # Calculate heading
                prevx, prevy = centers[i-1]
                dx = cx - prevx
                dy = cy - prevy
                angle = 0
                # Convert dx,dy to turtle heading (0 is east, 90 is north)
                if abs(dx) > abs(dy):
                    # horizontal move
                    angle = 0 if dx > 0 else 180
                else:
                    angle = 90 if dy > 0 else 270

                agent.setheading(angle)
                agent.goto(cx, cy)
                time.sleep(delay)

            # Keep window open until user closes
            screen.textinput('Done', 'Path animation complete. Press Enter to close.')
            turtle.bye()
        except Exception as e:
            print(f"Turtle visualization failed: {e}\nFalling back to matplotlib display.")
            # Fallback to matplotlib visualization
            self.visualize_solution(path)

def main():
    """Main function to run the maze solver"""

    # Define the maze (can be modified)
    maze = [
        [0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 1, 0, 1, 1],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0]
    ]

    print("=== MAZE REPRESENTATION ===")
    print("0 = walkable path (white)")
    print("1 = wall (black)")
    print()
    maze_array = np.array(maze)
    for i, row in enumerate(maze_array):
        print(f"Row {i:2d}: {' '.join(map(str, row))}")

    # Create and run solver
    solver = MazeSolver(maze)

    # Solve the maze
    solution_path = solver.solve()

    if solution_path:
        solver.print_solution_steps(solution_path)
        solver.visualize_solution(solution_path)

        # Try turtle visualization as well (interactive)
        try:
            solver.visualize_with_turtle(solution_path)
        except Exception:
            # visualize_with_turtle already falls back to matplotlib on error
            pass

        print(f"\n=== SOLUTION SUMMARY ===")
        print(f"Total steps in solution: {len(solution_path)}")
        print(f"Start position: {solver.start_pos}")
        print(f"End position: {solver.end_pos}")
        print("Image saved as 'maze_solution.png'")
    else:
        print("\nNo solution found for this maze configuration!")

if __name__ == "__main__":
    main()
