try:
    import numpy as np
    import matplotlib.pyplot as plt
    (x1, x2, x, y) = (float(i) for i in input('''
-- Input --

x1 x2 x y

x1: (Float) X intercept 1 of f(x)=Ax^2+Bx+C. 
x2: (Float) X intercept 2 of f(x)=Ax^2+Bx+C. Can be same with x1. 
x:  (Float) X value of a dot on f(x)=Ax^2+Bx+C. If k1 is a fixed 1, input 114.  
y:  (Float) Y value of a dot on f(x)=Ax^2+Bx+C. If k1 is a fixed 1, input 514.


-- Output --

k1 k2 k3

k1: (Float) A in f(x)=Ax^2+Bx+C.
k2: (Float) B in f(x)=Ax^2+Bx+C.
k3: (Float) C in f(x)=Ax^2+Bx+C.


-- Graphic Output --

(Matplotlib Graph)

1:  (Line plot) X axis.
2:  (Line plot) Graph of f(x)=Ax^2+Bx+C.
3:  (Scattered) Points of (x1, 0), (x2, 0), and (x, y). 


-- Example --

Input: 0 4 3 9        Output: -3.0 12.0 0.0 [Graph]
Input: 3 3 0 -9       Output: -1.0 6.0 -9.0 [Graph]
Input: 0.5 4 114 514  Output: 1.0 -4.5 2.0 [Graph]


-- Input below with the format above --

''').split())
    print()
    k2 = - x1 - x2
    k3 = x1 * x2
    if x == 114 and y == 514:
        k1 = 1.0
        ma = max(x1, x2)+1
        mi = min(x1, x2)-1
    else: 
        k1 = y / (x ** 2 + k2 * x + k3)
        plt.scatter(x, y, c='#1f77b4')
        ma = max(x1, x2, x)+1
        mi = min(x1, x2, x)-1
    for i in tuple(map(lambda x: round(x, 5), (k1, k1*k2, k1*k3))):
        print(i, end=" ")
    xarr = np.linspace(mi, ma, 1024)
    yarr = k1 * (xarr ** 2) + k1*k2 * xarr + k1*k3
    plt.plot(xarr, yarr)
    plt.plot([mi, ma], [0, 0], 'black')
    plt.scatter([x1, x2], [0, 0], c='#1f77b4')
    plt.show()
    
except ValueError as err:
    print(f"\nError: Wrong input - {err}")
except ZeroDivisionError as err:
    print(f"\nError: Invalid data - {err}")
except ModuleNotFoundError as err:
    print(f"\nError: Please install module - {err}")
except KeyboardInterrupt:
    print(f"\nProgram stopped manually")
except BaseException:
    print(f"\nUnknown Error")
