import sys
import json


def sets():
    a = [1,2,3,4,5,5,5,5]
    b = [5,6,7,8,9]

    print set(a)
    print list(set(a).intersection(set(b)))

def dictionaries():
    dict = { 'a': 'whatever', 'b': "now", 'c': "later"}
    print dict['a']


def main():
  sets()
  dictionaries()

main()
