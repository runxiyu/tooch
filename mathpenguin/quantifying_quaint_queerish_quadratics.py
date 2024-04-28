try:
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


-- Example --

Input: 0 4 3 9        Output: -3.0 12.0 0.0
Input: 3 3 0 -9       Output: -1.0 6.0 -9.0
Input: 0.5 4 114 514  Output: 1.0 -4.5 2.0


-- Input below with the format above --

''').split())
    print()
    k2 = - x1 - x2
    k3 = x1 * x2
    if x == 114 and y == 514:
        print(1.0, k2, k3)
    else: 
        k1 = y / (x ** 2 + k2 * x + k3)
        print(k1, k1*k2, k1*k3)
    
except ValueError as err:
    print(f"\nError: wrong input - {err}")
except ZeroDivisionError as err:
    print(f"\nError: Invalid data - {err}")
except KeyboardInterrupt:
    print(f"\nProgram stopped manually")
except BaseException:
    print(f"\nUnknown Error")
