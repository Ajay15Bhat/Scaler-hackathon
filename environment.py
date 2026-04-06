class WarehouseEnv:
    def __init__(self):
        self.GRID_SIZE = 5

        # Warehouse Grid (D = Drop Zone)
        self.grid = [
            ["S", ".", "A", ".", "D"],
            [".", "X", ".", ".", "B"],
            [".", ".", ".", ".", "."],
            ["C", ".", "X", ".", "."],
            [".", ".", ".", ".", "."]
        ]

        self.max_capacity = 2

        self.actions = [
            "move_up", "move_down", "move_left", "move_right",
            "pick_item", "deliver"
        ]

        self.reset()

    # ------------------------
    # RESET
    # ------------------------
    def reset(self):
        self.state = {
            "agent_position": [0, 0],
            "orders": [["A", "B"], ["C"]],
            "current_order": None,
            "item_locations": {},
            "inventory": [],
            "orders_completed": 0,
            "time": 0,
            "battery": 100
        }

        self.find_items()
        return self.state

    # ------------------------
    # FIND ITEMS
    # ------------------------
    def find_items(self):
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                val = self.grid[i][j]
                if val in ["A", "B", "C"]:
                    self.state["item_locations"][val] = [i, j]

    # ------------------------
    # MOVE
    # ------------------------
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

        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            if self.grid[row][col] != "X":
                self.state["agent_position"] = [row, col]

    # ------------------------
    # PICK ITEM
    # ------------------------
    def pick_item(self):
        pos = self.state["agent_position"]

        # Capacity constraint
        if len(self.state["inventory"]) >= self.max_capacity:
            return False, "capacity_full"

        for item, loc in self.state["item_locations"].items():
            if loc == pos and item not in self.state["inventory"]:
                self.state["inventory"].append(item)
                return True, item

        return False, None

    # ------------------------
    # DELIVERY CHECK
    # ------------------------
    def at_drop_zone(self):
        r, c = self.state["agent_position"]
        return self.grid[r][c] == "D"

    # ------------------------
    # STEP FUNCTION
    # ------------------------
    def step(self, action):
        reward = 0

        # Movement
        if action in ["move_up", "move_down", "move_left", "move_right"]:
            self.move(action)
            reward -= 0.1

        # Pick Item
        elif action == "pick_item":
            picked, item = self.pick_item()

            if picked:
                # Check if item is needed in current order
                if self.state["current_order"] and item in self.state["current_order"]:
                    reward += 2
                else:
                    reward -= 1  # wrong item
            else:
                reward -= 1

        # Deliver
        elif action == "deliver":
            if self.at_drop_zone() and self.state["current_order"]:
                if set(self.state["inventory"]) == set(self.state["current_order"]):
                    reward += 5
                    self.state["orders_completed"] += 1
                    self.state["inventory"] = []
                    self.state["current_order"] = None
                else:
                    reward -= 2  # incomplete delivery
            else:
                reward -= 2

        # Auto-assign next order if none
        if self.state["current_order"] is None and self.state["orders"]:
            self.state["current_order"] = self.state["orders"].pop(0)

        # Time + battery
        self.state["time"] += 1
        self.state["battery"] -= 1

        # Done conditions
        done = False

        if self.state["orders_completed"] >= 2:
            reward += 10
            done = True

        if self.state["battery"] <= 0 or self.state["time"] > 100:
            done = True

        return self.state, reward, done, {}

    # ------------------------
    # STATE FUNCTION (for API)
    # ------------------------
    def get_state(self):
        return self.state
