from server.models import State


class WarehouseEnv:
    def __init__(self):
        self.GRID_SIZE = 5

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
            "pick_item", "get_order", "complete_order"
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
        r, c = self._state["agent_position"]

        if action == "move_up":
            r -= 1
        elif action == "move_down":
            r += 1
        elif action == "move_left":
            c -= 1
        elif action == "move_right":
            c += 1

        if 0 <= r < self.GRID_SIZE and 0 <= c < self.GRID_SIZE:
            if self.grid[r][c] != "X":
                self._state["agent_position"] = [r, c]

    # ------------------------
    # PICK ITEM (IMPROVED 🔥)
    # ------------------------
    def pick_item(self):
        pos = self._state["agent_position"]

        if len(self._state["inventory"]) >= self.max_capacity:
            return False, "capacity_full"

        for item, loc in self._state["item_locations"].items():
            if loc == pos:
                if item in self._state["inventory"]:
                    return False, "already_picked"

                self._state["inventory"].append(item)

                # Reward shaping
                if self._state["current_order"] and item in self._state["current_order"]:
                    return True, "correct"
                else:
                    return True, "wrong_item"

        return False, "no_item"

    # ------------------------
    # DROP ZONE CHECK
    # ------------------------
    def at_drop_zone(self):
        r, c = self._state["agent_position"]
        return self.grid[r][c] == "D"

    # ------------------------
    # STEP FUNCTION (UPGRADED 🔥)
    # ------------------------
    def step(self, action):
        reward = 0

        # Movement
        if action.startswith("move"):
            prev_pos = self._state["agent_position"].copy()
            self.move(action)

            if self._state["agent_position"] == prev_pos:
                reward -= 0.3  # hitting wall penalty
            else:
                reward -= 0.1

        # Get Order
        elif action == "get_order":
            if self._state["current_order"] is None and self._state["orders"]:
                self._state["current_order"] = self._state["orders"].pop(0)
                reward += 2  # stronger incentive
            else:
                reward -= 1

        # Pick Item
        elif action == "pick_item":
            success, reason = self.pick_item()

            if success:
                if reason == "correct":
                    reward += 3
                elif reason == "wrong_item":
                    reward -= 2
            else:
                reward -= 2

        # Complete Order
        elif action == "complete_order":
            if self.at_drop_zone() and self._state["current_order"]:
                if set(self._state["inventory"]) == set(self._state["current_order"]):
                    reward += 10
                    self._state["orders_completed"] += 1
                    self._state["inventory"] = []
                    self._state["current_order"] = None
                else:
                    reward -= 4
            else:
                reward -= 3

        else:
            reward -= 2

        # Time & battery
        self._state["time"] += 1
        self._state["battery"] -= 1

        # Done conditions
        done = False

        if not self._state["orders"] and self._state["current_order"] is None:
            reward += 20  # BIG completion bonus
            done = True

        if self._state["battery"] <= 0 or self._state["time"] > 150:
            done = True

        return self.state(), reward, done, {}

    # ------------------------
    # STATE OUTPUT
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
