import turtle
import math

def dent_edge_inward(t, length, depth):
    if depth == 0:
        t.forward(length)
        return
    l = length / 3.0
    dent_edge_inward(t, l, depth - 1)
    t.right(60)
    dent_edge_inward(t, l, depth - 1)
    t.left(120)
    dent_edge_inward(t, l, depth - 1)
    t.right(60)
    dent_edge_inward(t, l, depth - 1)

def fractal_polygon(sides, length, depth):
    scr = turtle.Screen()
    scr.bgcolor("white")
    t = turtle.Turtle(visible=False)
    t.speed(0)
    turtle.tracer(False)

    apothem = length / (2 * math.tan(math.pi / sides))
    t.penup()
    t.setpos(-length/2, -apothem)
    t.setheading(0)
    t.pendown()

    turn = 360 / sides
    for _ in range(sides):
        dent_edge_inward(t, length, depth)
        t.right(turn)

    turtle.tracer(True)
    turtle.done()

sides = int(input("Enter the number of sides: "))
length = int(input("Enter the side length: "))
depth = int(input("Enter the recursion depth: "))
fractal_polygon(sides, length, depth)
