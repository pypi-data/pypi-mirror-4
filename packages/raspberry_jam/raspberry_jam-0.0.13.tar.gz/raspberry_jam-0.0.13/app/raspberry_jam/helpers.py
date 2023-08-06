from raspberry_jam import app

def yield_first(iterable):
    for item in iterable or []:
        yield item
        return

def chunk(list, n):
    # Split list into chunks of n size
    return [list[i:i+n] for i in range(0, len(list), n)]
