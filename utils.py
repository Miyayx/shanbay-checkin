
def rand_pause():
    import random
    d = random.randint(20, 100);
    import time
    time.sleep(d)
    return d

def timestamp():
    import time
    return int(time.time()) * 1000

