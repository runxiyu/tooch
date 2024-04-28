from math import *

def f():
    # Angle Opposite Adjacent
    (x, a, b) = (float(x) for x in input().split())
    if a >= b:  
        y = round(degrees(asin(sin(radians(x))/a*b)), 1)
        x = round(x, 1)
        z = round(180 - x - y, 1)
        print(x, y, z)
    else:
        y1 = round(degrees(asin(sin(radians(x))/a*b)), 1)
        y2 = round(degrees(pi-asin(sin(radians(x))/a*b)), 1)
        x = round(x, 1)
        z1 = round(180 - x - y1, 1)
        z2 = round(180 - x - y2, 1)
        print(x, y1, z1)
        print(x, y2, z2)

try: 
    while True: 
        f()
except KeyboardInterrupt:
    print("Program Exited")
except BaseException as e:
    print("Error:", e)
