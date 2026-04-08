def grade(state: dict) -> float:
    if not state:
        return 0.0

    orders_completed = state.get("orders_completed", 0)
    time_taken = state.get("time", 150)
    battery_left = state.get("battery", 0)

    score = 0.0

    # ------------------------
    # Orders Completed (VERY IMPORTANT)
    # ------------------------
    score += orders_completed * 80

    # ------------------------
    # Time Efficiency (STRONGER 🔥)
    # ------------------------
    time_score = max(0, 80 - time_taken * 0.7)
    score += time_score

    # ------------------------
    # Battery Efficiency
    # ------------------------
    battery_score = battery_left * 0.3
    score += battery_score

    # ------------------------
    # Bonus for perfect run
    # ------------------------
    if orders_completed >= 2 and time_taken < 40:
        score += 20

    return round(score, 2)
