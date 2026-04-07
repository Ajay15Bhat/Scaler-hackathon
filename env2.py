from models import State


class WarehouseEnv:
    def __init__(self):
        self.GRID_SIZE = 5

        # Warehouse Grid
        self.grid = [
            ["S", ".", "A", ".", "D"],
            [".", "X", ".", ".", "B"],
            [".", ".", ".", ".", "."],
            ["C", ".", "X", ".", "."],
            [".", ".", ".", ".", "."]
        ]

        self.max_capacity = 2

        self.actions = [
            "move_up",
            "move_down",
            "move_left",
            "move_right",
            "pick_item",
            "deliver",
            "get_order",
            "complete_order"
        ]

        self.reset()

    # ------------------------
    # RESET
    # ------------------------
    def reset(self):
        self._state = {
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
        return self.state()

    # ------------------------
    # FIND ITEMS
    # ------------------------
    def find_items(self):
        for i in range(self.GRID_SIZE):
            for j in range(self.GRID_SIZE):
                val = self.grid[i][j]
                if val in ["A", "B", "C"]:
                    self._state["item_locations"][val] = [i, j]

    # ------------------------
    # MOVE
    # ------------------------
    def move(self, action):
        row, col = self._state["agent_position"]

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
                self._state["agent_position"] = [row, col]

    # ------------------------
    # PICK ITEM
    # ------------------------
    def pick_item(self):
        pos = self._state["agent_position"]

        if len(self._state["inventory"]) >= self.max_capacity:
            return False, "capacity_full"

        for item, loc in self._state["item_locations"].items():
            if loc == pos and item not in self._state["inventory"]:
                self._state["inventory"].append(item)
                return True, item

        return False, None

    # ------------------------
    # DROP ZONE
    # ------------------------
    def at_drop_zone(self):
        r, c = self._state["agent_position"]
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

        # Get Order
        elif action == "get_order":
            if self._state["current_order"] is None and self._state["orders"]:
                self._state["current_order"] = self._state["orders"].pop(0)
                reward += 1
            else:
                reward -= 0.5

        # Pick Item
        elif action == "pick_item":
            picked, item = self.pick_item()

            if picked:
                if self._state["current_order"] and item in self._state["current_order"]:
                    reward += 2
                else:
                    reward -= 1
            else:
                reward -= 1

        # Deliver / Complete
        elif action in ["deliver", "complete_order"]:
            if self.at_drop_zone() and self._state["current_order"]:
                if set(self._state["inventory"]) == set(self._state["current_order"]):
                    reward += 5
                    self._state["orders_completed"] += 1
                    self._state["inventory"] = []
                    self._state["current_order"] = None
                else:
                    reward -= 2
            else:
                reward -= 2

        # Invalid Action (NEW FIX)
        else:
            reward -= 1

        # Auto assign order
        if self._state["current_order"] is None and self._state["orders"]:
            self._state["current_order"] = self._state["orders"][0]

        # Time + Battery
        self._state["time"] += 1
        self._state["battery"] -= 1

        # Episode Logic
        done = False

        # All orders completed
        if not self._state["orders"] and self._state["current_order"] is None:
            reward += 10
            done = True

        # Battery finished
        if self._state["battery"] <= 0:
            done = True

        # Time limit
        if self._state["time"] > 100:
            done = True

        return self.state(), reward, done, {}

    # ------------------------
    # STATE (OpenEnv)
    # ------------------------
    def state(self):
        return State(
            agent_position=self._state["agent_position"],
            inventory=self._state["inventory"],
            current_order=self._state["current_order"],
            orders_completed=self._state["orders_completed"],
            time=self._state["time"],
            battery=self._state["battery"]
        ).model_dump()