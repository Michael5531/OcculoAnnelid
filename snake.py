"""
Taken and modified from the code at https://github.com/grantjenks/free-python-games.
"""

from turtle import *
from random import randrange
from freegames import square, vector

food = vector(0, 0)
snake = [vector(10, 0)]
aim = vector(0, -10)


def change(x, y):
    """Change snake direction."""
    aim.x = x
    aim.y = y


def inside(head):
    """Return True if head inside boundaries."""
    return -200 < head.x < 190 and -200 < head.y < 190


def move(label, snake_direction):
    """Move snake forward one segment."""

    snake_direction = change_direction(label, snake_direction)

    head = snake[-1].copy()
    head.move(aim)

    if not inside(head) or head in snake:
        square(head.x, head.y, 9, 'red')
        update()
        return

    snake.append(head)

    if head == food:
        print('Snake:', len(snake))
        food.x = randrange(-15, 15) * 10
        food.y = randrange(-15, 15) * 10
    else:
        snake.pop(0)

    clear()

    for body in snake:
        square(body.x, body.y, 9, 'black')

    square(food.x, food.y, 9, 'green')
    update()

    return snake_direction


def change_direction(classifier_label, direction):

    # case: Up
    if classifier_label == "Right" and direction == "Up":
        change(10, 0)
        direction = "Right"
    elif classifier_label == "Left" and direction == "Up":
        change(-10, 0)
        direction = "Left"
    # case: Down
    elif classifier_label == "Right" and direction == "Down":
        change(-10, 0)
        direction = "Left"
    elif classifier_label == "Left" and direction == "Down":
        change(10, 0)
        direction = "Right"
    # case: Right
    elif classifier_label == "Right" and direction == "Right":
        change(0, -10)
        direction = "Down"
    elif classifier_label == "Left" and direction == "Right":
        change(0, 10)
        direction = "Up"
    # case: Left
    elif classifier_label == "Right" and direction == "Left":
        change(0, 10)
        direction = "Up"
    elif classifier_label == "Left" and direction == "Left":
        change(0, -10)
        direction = "Down"
    # else: maintain current direction
    else:
        pass

    print("Current direction: {}".format(direction))

    return direction
