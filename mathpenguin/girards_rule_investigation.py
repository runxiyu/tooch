from math import sqrt

K = list(range(2, 9))

for k in K:
    N = 4 * k + 1
    print(f"\nk: {k}\tN: {N}")
    for a in range(1, int(sqrt(N))+1):
        for b in range(1, int(sqrt(N-a**2))+1):
            if b**2 == (N - a**2): 
                print(f"a: {a}\tb: {b}")
