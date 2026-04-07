def grade(state):
    """
    Returns a score between 0 and 1 based on:
    - task completion
    - efficiency (time)
    - battery usage
    - small penalty for no progress
    """

    if not state:
        return 0.0

    # -------------------------
    # 1. COMPLETION SCORE (50%)
    # -------------------------
    orders_completed = state.get("orders_completed", 0)

    # You can adjust this dynamically if needed
    total_orders = max(1, len(state.get("current_order") or []) + orders_completed)

    completion_score = orders_completed / total_orders
    completion_score = min(completion_score, 1.0)

    # -------------------------
    # 2. EFFICIENCY SCORE (30%)
    # -------------------------
    time_taken = state.get("time", 100)

    # Faster = better
    efficiency_score = max(0, 1 - (time_taken / 100))

    # -------------------------
    # 3. BATTERY SCORE (15%)
    # -------------------------
    battery = state.get("battery", 100)
    battery_score = max(0, battery / 100)

    # -------------------------
    # 4. ACTIVITY BONUS (5%)
    # -------------------------
    # Penalize if agent did nothing useful
    moved = state.get("time", 0) > 0
    has_inventory = len(state.get("inventory", [])) > 0

    activity_score = 0.05 if (moved or has_inventory or orders_completed > 0) else 0

    # -------------------------
    # FINAL WEIGHTED SCORE
    # -------------------------
    score = (
        0.5 * completion_score +
        0.3 * efficiency_score +
        0.15 * battery_score +
        activity_score
    )

    # Clamp between 0 and 1
    score = max(0, min(score, 1))

    return round(score, 3)