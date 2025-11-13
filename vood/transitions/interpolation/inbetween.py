def inbetween(start, end, num):
    step = (end - start) / (num + 1)
    return [start + step * (i + 1) for i in range(num)]
