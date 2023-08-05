"""Helper functions for Problem 27"""
import numbers, math, fractions

def isPrime(n):
    if not isinstance(n, numbers.Integral):
        # only positive integers can be prime
        return False
    return n > 0 and len(factors(n, isPrime=True)) == 1

def factors(n, isPrime=False):
    # given a number n, return a list of its prime factorization
    # factors(360) = [2, 2, 2, 3, 3, 5] in order
    #
    # non-integer numbers will truncate
    #
    # if isPrime is true, returns as soon as the factorlist length
    # is greater than 1
    n = math.trunc(n)  # should truncate
    factorlist = []
    i = 2
    j = n
    if j < 0:
        # negatives start with -1 as a factor
        factorlist.append(-1)
        j //= -1
    while i * i <= j:
        if isPrime and len(factorlist) > 1:
            # short-circuit for primality testing
            return factorlist
        if j % i == 0:
            factorlist.append(i)
            j //= i
        else:
            i += 1
    if j > 1:
        factorlist.append(j)
    return factorlist

def primes(n):
    # returns all primes less than n (assuming n is positive)
    # using the Sieve of Eratosthenes
    assert n >= 0
    sieve = [x for x in range(n)]
    if len(sieve) <= 0:
        return []
    sieve[0] = False
    sieve[1] = False
    i = 2
    while i*i < n:
        if i:
            j = 0
            nextnum = i*i + j*i
            while nextnum < n:
                sieve[nextnum] = False
                j += 1
                nextnum = i*i + j*i
        i += 1
    return list(filter(None, sieve))
