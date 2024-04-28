from math import *

def f():
    # Angle Adjacent1 Adjacent2
    (x, a, b) = (float(x) for x in input().split())
    print(round(a*b*sin(radians(x))/2, 3))

try: 
    while True: 
        f()
except KeyboardInterrupt:
    print("Program Exited")
except BaseException as e:
    print("Error:", e)
