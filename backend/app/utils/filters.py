def smooth(old, new, factor=0.2):
    return old * (1 - factor) + new * factor
