from math import *

def f():
    # Angle Adjacent1 Adjacent2
    (x, a, b) = (float(x) for x in input().split())
    tmp = a**2 + b**2 - 2*a*b*cos(radians(x))
    sqrttmp = round(sqrt(tmp), 3)
    tmp = round(tmp, 3)
    print(f"sqrt({tmp}) = {sqrttmp}")

try: 
    while True: 
        f()
except KeyboardInterrupt:
    print("Program Exited")
except BaseException as e:
    print("Error:", e)
