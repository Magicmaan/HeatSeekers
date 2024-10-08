from mqtt import awtBroker, awtConnection


def test():
    m = awtConnection("test", "test", "test", "test")
    awtBroker()

test()