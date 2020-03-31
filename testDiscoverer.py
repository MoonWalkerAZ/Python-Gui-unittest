import json
import unittest


def consume(iterable):
    input = list(iterable)
    while input:
        item = input.pop(0)
        try:
            data = iter(item)
            input = list(data) + input
        except:
            yield item


def discover_tests(imeDatoteke):
    '''
    Collect a list of potentially runnable tests
    '''
    imenaTestov = []
    loader = unittest.TestLoader()
    suite = loader.discover(imeDatoteke)

    for test in list(consume(suite)):
        #print(test.id())
        imenaTestov.append(test.id())
    return imenaTestov


def isciTeste(imeDatoteke):
    imenaTestov = discover_tests(imeDatoteke)
    return imenaTestov