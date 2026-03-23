"""Simple script to test if VS Code debugger works."""


def add(a: int, b: int) -> int:
    result = a + b      # <-- put breakpoint here (line 5)
    return result


def main():
    x = add(2, 3)
    print(f"2 + 3 = {x}")

    y = add(10, 20)
    print(f"10 + 20 = {y}")


if __name__ == "__main__":
    main()
