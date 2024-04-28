from math import *

def f():
    # Side Opposite Adjacent
    (x, a, b) = (float(i) for i in input().split())
    y = round(x/sin(radians(a))*sin(radians(b)), 1)
    print(y)

try: 
    while True: 
        f()
except KeyboardInterrupt:
    print("Program Exited")
except BaseException as e:
    print("Error:", e)
