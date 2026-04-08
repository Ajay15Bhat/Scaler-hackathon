def grade(state: dict) -> float:
    if not state:
        return 0.0

    orders_completed = state.get("orders_completed", 0)
    time_taken = state.get("time", 100)
    battery_left = state.get("battery", 0)

    completion = orders_completed / 2   # normalize (max 2 orders)
    efficiency = max(0, 1 - time_taken / 100)
    battery = battery_left / 100

    score = 0.5 * completion + 0.3 * efficiency + 0.2 * battery

    return round(min(max(score, 0), 1), 3)