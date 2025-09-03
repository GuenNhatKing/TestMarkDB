import secrets
import time

base62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def randomX(n, low, high):
    for _ in range(n):
        yield low + secrets.randbelow(high - low)

def randomOTP():
    return ''.join(map(str, [x for x in randomX(4, 0, 10)]))

def randomFileName():
    return f'{str(time.time())}.{''.join(map(str, [base62[x] for x in randomX(24, 0, 62)]))}'