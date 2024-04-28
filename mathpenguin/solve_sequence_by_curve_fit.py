#!/usr/bin/env python3


from scipy.optimize import curve_fit


def f1(x, k1, k0):
    return k1 * x + k0


def f2(x, k3, k2, k1, k0):
    return k3 * x**3 + k2 * x**2 + k1 * x + k0


def f3(x, k3, k2, k1, k0, k2_, k3_):
    return k3 * x**3 + k2 * x**2 + k1 * x + k0 + k2_ * 2**x + k3_ * 3**x


def main(x, l):
    if l < 4:
        (a), _ = curve_fit(f1, list(range(1, l + 1)), x)
        a = list(map(lambda x: round(x, 4), a))
        (k1, k0) = a
        print(f"U_n = {k1} n + {k0}")
        for i in range(1, 11):
            print(round(f1(i, k1, k0), 3), end=" ")
    elif l < 6:
        (a), _ = curve_fit(f2, list(range(1, l + 1)), x)
        a = list(map(lambda x: round(x, 4), a))
        (k3, k2, k1, k0) = a
        print(f"U_n = {k3} n^3 + {k2} n^2 + {k1} n + {k0}")
        for i in range(1, 16):
            print(round(f2(i, k3, k2, k1, k0), 3), end=" ")
    else:
        (a), _ = curve_fit(f3, list(range(1, 7)), x)
        a = list(map(lambda x: round(x, 4), a))
        (k3, k2, k1, k0, k2_, k3_) = a
        print(f"U_n = {k3_} 3^n + {k2_} 2^n + {k3} n^3 + {k2} n^2 + {k1} n + {k0}")
        for i in range(1, 21):
            print(round(f3(i, k3, k2, k1, k0, k2_, k3_), 2), end=" ")
        print()


x = list(input("Enter Numbers: ").split())
if len(x) < 2:
    print("Size of sequence too small (<2) or sequence not entered correctly")
elif len(x) < 4:
    x = list(map(int, x))
    main(x, len(x))
elif len(x) < 6:
    x = list(map(int, x))
    main(x, len(x))
else:
    x = list(map(int, x))[0:6]
    main(x, 6)
