def parse_int(value, default = -1):
    try:
        result = int(value)
    except ValueError:
        result = default
