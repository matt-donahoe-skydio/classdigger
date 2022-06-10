"""
Example code from this blog
https://gaopinghuang0.github.io/2018/12/29/dig-into-python-super-and-mro

It surprised me.
"""
class A(object):
    def go(self):
        print("A")

class O(object):
    def go(self):
        print("O")

class B(A):
    def go(self):
        print("B1")
        super(B, self).go()
        print("B2")

class C(A):  # Change A to O and you'll get something else.
    def go(self):
        print("C1")
        super(C, self).go()
        print("C2")

class D(B,C):
    def go(self):
        print("D1")
        super(D, self).go()
        print("D2")

D().go()
