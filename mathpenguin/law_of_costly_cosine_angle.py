from math import *

def f():
    # Opposite Adjacent1 Adjacent2
    (c, a, b) = (float(x) for x in input().split())
    print(round(degrees(acos((a**2 + b**2 - c**2) / (2*a*b))), 1))

try: 
    while True: 
        f()
except KeyboardInterrupt:
    print("Program Exited")
except BaseException as e:
    print("Error:", e)
