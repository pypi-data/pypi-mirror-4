#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Dell
#
# Created:     11/02/2013
# Copyright:   (c) Dell 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
def subs(st):
    st = list(st)
    arr = []
    i = 0
    while i < len(st):
        j = i
        n = 0
        while j < len(st):
            arr.append("".join(st[n:i+n+1]))
            j += 1
            n += 1
        i += 1
    return arr

def main():
    n = int(raw_input())
    h = 0
    joinst = []
    while h < n:
        s1 = raw_input()
        joinst += subs(s1)
        h += 1
    joinst = sorted(set(joinst))
    aa = int(raw_input())
    ii = 0
    while ii < aa:
        nn = int(raw_input())
        try:
            print joinst[nn-1]
            ii += 1
        except:
            print "INVALID"
            ii += 1

if __name__ == '__main__':
    main()
