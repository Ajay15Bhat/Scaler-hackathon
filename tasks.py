def easy_task():
    return {
        "orders": [["A"]],
        "max_steps": 30,
        "battery": 100
    }


def medium_task():
    return {
        "orders": [["A", "B"]],
        "max_steps": 60,
        "battery": 80
    }


def hard_task():
    return {
        "orders": [["A", "B"], ["C"]],
        "max_steps": 100,
        "battery": 50
    }


TASKS = {
    "easy": easy_task,
    "medium": medium_task,
    "hard": hard_task
}
