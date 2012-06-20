# http://stackoverflow.com/questions/36932/\
#        whats-the-best-way-to-implement-an-enum-in-python


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)
