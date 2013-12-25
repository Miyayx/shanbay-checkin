
def rand_pause():
    import random
    d = random.randint(60, 300);
    import time
    time.sleep(d)

def timestamp():
    import time
    return int(time.time()) * 1000

