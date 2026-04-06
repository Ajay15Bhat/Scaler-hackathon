class WarehouseEnv:
    def __init__(self):
        self.GRID_SIZE = 5

        # Warehouse Grid
        self.grid = [
            ["S", ".", "A", ".", "."],
            [".", "X", ".", ".", "B"],
            [".", ".", ".", ".", "."],
            ["C", ".", "X", ".", "."],
            [".", ".", ".", ".", "."]
        ]

        # Environment State
        self.state = {
            "agent_position": [0, 0],
            "orders": ["A", "B", "C"],
            "current_order": None,
            "item_locations": {},
            "picked_items": [],
            "time": 0,
            "battery": 100
        }

        # Available Actions
        self.actions = [
            "move_up",
            "move_down",
            "move_left",
            "move_right",
            "pick_item"
        ]

        # Find Item Locations
        self.find_items()

    def find_items(self):
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                if self.grid[i][j] in ["A", "B", "C"]:
                    self.state["item_locations"][self.grid[i][j]] = [i, j]

    def reset(self):
        self.state["agent_position"] = [0, 0]
        self.state["picked_items"] = []
        self.state["time"] = 0
        self.state["battery"] = 100

        return self.state

    def move(self, action):
        row, col = self.state["agent_position"]

        if action == "move_up":
            row -= 1

        elif action == "move_down":
            row += 1

        elif action == "move_left":
            col -= 1

        elif action == "move_right":
            col += 1

        # Boundary + obstacle check
        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            if self.grid[row][col] != "X":
                self.state["agent_position"] = [row, col]

    def pick_item(self):
        pos = self.state["agent_position"]

        for item, location in self.state["item_locations"].items():
            if location == pos and item not in self.state["picked_items"]:
                self.state["picked_items"].append(item)
                return True

        return False

    def step(self, action):
        reward = 0

        # Movement
        if action in ["move_up", "move_down", "move_left", "move_right"]:
            self.move(action)
            reward -= 0.1

        # Pick item
        elif action == "pick_item":
            picked = self.pick_item()

            if picked:
                reward += 2
            else:
                reward -= 1

        # Update time + battery
        self.state["time"] += 1
        self.state["battery"] -= 1

        # Done condition
        done = False

        if len(self.state["picked_items"]) == len(self.state["orders"]):
            done = True

        if self.state["time"] > 50:
            done = True

        if self.state["battery"] <= 0:
            done = True

        return self.state, reward, done, {}