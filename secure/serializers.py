from rest_framework.response import Response


def zddpaginate(page=1, count=5):
    count = 15 if count >= 15 else count
    start = page - 1
    start = start * count
    if start < 0 or count < 0:
        return start, count, False
    return start, count ,True