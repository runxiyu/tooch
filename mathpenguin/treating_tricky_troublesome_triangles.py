from math import *
import time


def angle_sum(a, b):
    return round(180-a-b, 5)

def cosine_angle(o, a, b):
    # Opposite Adjacent1 Adjacent2
    return round(degrees(acos((a**2 + b**2 - o**2) / (2*a*b))), 5)

def cosine_side(x, a, b):
    # Angle Adjacent1 Adjacent2
    return round(sqrt(a**2 + b**2 - 2*a*b*cos(radians(x))), 5)

def sine_side(s, o, a):
    # Side Opposite Adjacent
    return round(s/sin(radians(o))*sin(radians(a)), 5)

def sine_angle(x, o, a):
    # Angle Opposite Adjacent
    if o >= a:  
        return [round(degrees(asin(sin(radians(x))/o*a)), 5), 0]
    else:
        return [round(degrees(asin(sin(radians(x))/o*a)), 5), round(degrees(pi-asin(sin(radians(x))/o*a)), 5)]

def sine_area(x, a, b):
    # Angle Adjacent1 Adjacent2
    return round(a*b*sin(radians(x))/2, 5)

def check(A, B, C, a, b, c):
    l = [A+B+C>179.9, A+B+C<180.1, a+b>c, a+c>b, b+c>a]
    for i in range(len(l)):
        return l[i]
    return True

def solve(A, B, C, a, b, c, singlesolution):
    start_time = time.time()
    while time.time() - start_time < 1 and not (A and B and C and a and b and c):
        if A and B and not C:
            C = angle_sum(A, B)
        if A and C and not B:
            B = angle_sum(A, C)
        if B and C and not A:
            A = angle_sum(B, C)
        if a and b and c:
            if not A:
                A = cosine_angle(a, b, c)
            if not B:
                B = cosine_angle(b, a, c)
            if not C:
                C = cosine_angle(c, a, b)
        if A and b and c and not a:
            a = cosine_side(A, b, c)
        if B and a and c and not b:
            b = cosine_side(B, a, c)
        if C and a and b and not c:
            c = cosine_side(C, a, b)
        if A and a:
            if B and not b:
                b = sine_side(a, A, B)
            if C and not c:
                c = sine_side(a, A, C)
            if b and not B:
                tmp = sine_angle(A, a, b)
                B = tmp[1]
                if B and singlesolution:
                    solve(A, B, C, a, b, c, False)
                    singlesolution = False
                    B = tmp[0]
                else:
                    B = tmp[0]
            if c and not C:
                tmp = sine_angle(A, a, c)
                C = tmp[1]
                if C and singlesolution:
                    solve(A, B, C, a, b, c, False)
                    singlesolution = False
                    C = tmp[0]
                else:
                    C = tmp[0]
        if B and b:
            if A and not a:
                a = sine_side(b, B, A)
            if C and not c:
                c = sine_side(b, B, C)
            if a and not A:
                tmp = sine_angle(B, b, a)
                A = tmp[1]
                if A and singlesolution:
                    solve(A, B, C, a, b, c, False)
                    singlesolution = False
                    A = tmp[0]
                else:
                    A = tmp[0]
            if c and not C:
                tmp = sine_angle(B, b, c)
                C = tmp[1]
                if C and singlesolution:
                    solve(A, B, C, a, b, c, False)
                    singlesolution = False
                    C = tmp[0]
                else:
                    C = tmp[0]
        if C and c:
            if A and not a:
                a = sine_side(c, C, A)
            if B and not b:
                b = sine_side(c, C, B)
            if a and not A:
                tmp = sine_angle(C, c, a)
                A = tmp[1]
                if A and singlesolution:
                    solve(A, B, C, a, b, c, False)
                    singlesolution = False
                    A = tmp[0]
                else:
                    A = tmp[0]
            if b and not B:
                tmp = sine_angle(C, c, b)
                B = tmp[1]
                if B and singlesolution:
                    solve(A, B, C, a, b, c, False)
                    singlesolution = False
                    B = tmp[0]
                else:
                    B = tmp[0]
    if time.time()-start_time > 1:
        print("Error: Time limit excceeded")
    elif check(A, B, C, a, b, c):
        print(f"\n∠{nameA}: {A}\n∠{nameB}: {B}\n∠{nameC}: {C}\n{nameA}{nameB}: {c}\n{nameA}{nameC}: {b}\n{nameB}{nameC}: {a}\nArea: {sine_area(A, b, c)}")

try:
    print("Please type know data below. \nSkip unknown data with enter. \n")
    nameA = input("Vertex 1: ")
    nameB = input("Vertex 2: ")
    nameC = input("Vertex 3: ")
    if not nameA:
        nameA = "A"
    if not nameB:
        nameB = "B"
    if not nameC:
        nameC = "C"
    A = input(f"∠{nameA}: ")
    B = input(f"∠{nameB}: ")
    C = input(f"∠{nameC}: ")
    c = input(f"{nameA}{nameB}: ")
    b = input(f"{nameA}{nameC}: ")
    a = input(f"{nameB}{nameC}: ")
    (A, B, C, a, b, c) = tuple(map(lambda x: float(x) if x else 0, (A, B, C, a, b, c)))
    solve(A, B, C, a, b, c, True)
except KeyboardInterrupt:
    print("Program exited")
except ValueError as e:
    print("Error: bad input,", e)
except BaseException as e:
    print("Error:", e)
