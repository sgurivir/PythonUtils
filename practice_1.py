

"""

Question:
Write a program which will find all such numbers which are divisible by 7 but are not a multiple of 5,
between 2000 and 3200 (both included).
The numbers obtained should be printed in a comma-separated sequence on a single line.

"""

results = []
for i in range(2000, 3200):
    if i % 7 == 0 and not i % 5 != 0:
        results.append(str(i))

print ",".join(results)


"""
Question:
Write a program which can compute the factorial of a given numbers.
8
Then, the output should be:
40320
"""


def factorial(n):
    if n == 0:
        return 1

    return n * factorial(n-1)

print factorial(8)

"""
Question:
With a given integral number n, write a program to generate a dictionary that contains (i, i*i) such that is an integral number between 1 and n (both included). and then the program should print the dictionary.
Suppose the following input is supplied to the program:
"""


def generate_square_dictionary(n):
    square_map = dict()

    for i in range(1, n):
        square_map[i] = i*i

    return square_map

print(generate_square_dictionary(10))


"""
Question 4
Level 1

Question:
Write a program which accepts a sequence of comma-separated numbers from console and generate a list and a tuple which contains every number.
Suppose the following input is supplied to the program:
34,67,55,33,12,98
Then, the output should be:
['34', '67', '55', '33', '12', '98']
('34', '67', '55', '33', '12', '98')
"""

import sys
arg = "2,3,4,5,6,7"
n_ls = arg.split(",")
n_ts = tuple(n_ls)

print n_ts
print n_ls


"""
Question:
Define a class which has at least two methods:
getString: to get a string from console input
printString: to print the string in upper case.
Also please include simple test function to test the class methods.
"""
class x(object):
    def x(self):
        pass

    def y(self):
        pass

    @staticmethod
    def z():
        pass


"""
Question 6
Level 2

Question:
Write a program that calculates and prints the value according to the given formula:
Q = Square root of [(2 * C * D)/H]
Following are the fixed values of C and H:
C is 50. H is 30.
D is the variable whose values should be input to your program in a comma-separated sequence.
Example
Let us assume the following comma separated input sequence is given to the program:
100,150,180
The output of the program should be:
18,22,24
"""

def formula(D):
    C = 50
    H = 30
    l = []
    for d in D.split(","):
        d = int(d)
        import math
        l.append(math.sqrt(2.0*C*d)/H)

    C = C + 1
    print C
    return ",".join(str(v) for v in l)

print formula("100,150,180")

"""
3,5
Then, the output of the program should be:
[[0, 0, 0, 0, 0], [0, 1, 2, 3, 4], [0, 2, 4, 6, 8]] 
"""

nr, nc = 3,5
matrix = [[0 for col in range(nc)] for row in range(nr)]
for i in range(0, nr-1):
    for j in range(0, nc-1):
        matrix[i][j] = i * j

x = [0 for col in range(nc)]
print x


"""
Question 8
Level 2

Question:
Write a program that accepts a comma separated sequence of words as input and prints the words in a comma-separated sequence after sorting them alphabetically.
Suppose the following input is supplied to the program:
without,hello,bag,world
Then, the output should be:
bag,hello,without,world
"""

def sort_words(word_list):
    items = word_list.split(" ")
    items.sort()
    print ",".join(items) # Note the join here

sort_words("i am writing python code")

"""
Question 9
Level 2
\prints the lines after making all characters in the sentence capitalized.
Suppose the following input is supplied to the program:
Hello world
Practice makes perfect
Then, the output should be:
HELLO WORLD
PRACTICE MAKES PERFECT
"""
s = "More guava makes world a better place"
print s.upper()

words = [word for word in s.split(" ")]
print words
print sorted(words)

"""
Question:
Write a program that accepts a sentence and calculate the number of letters and digits.
Suppose the following input is supplied to the program:
hello world! 123
Then, the output should be:
LETTERS 10
DIGITS 3
"""
def num_digits_and_letters(s):
    counts = {"DIGITS":0, "LETTERS":0}
    for c in s:
        if c.is_digit():
            counts["DIGITS"]+=1
        else:
            counts["LETTERS"]+=1

"""
Question 10
Level 2

Question:
Write a program that accepts a sequence of whitespace separated words as input and prints the words after removing all duplicate words and sorting them alphanumerically.
Suppose the following input is supplied to the program:
hello world and practice makes perfect and hello world again
Then, the output should be:
again and hello makes perfect practice world
"""

sentence = "Quick A B C Quick L D ERF B"
words = sentence.split(" ")
print " ".join(set(words))

"""
Question 11
Level 2

Question:
Write a program which accepts a sequence of comma separated 4 digit binary numbers as its input and then check whether they are divisible by 5 or not. 
The numbers that are divisible by 5 are to be printed in a comma separated sequence.
Example:
0100,0011,1010,1001
Then the output should be:
1010
Notes: Assume the data is input by console.
"""
input = "0100,0011,1010,1001"
words = [x for x in input.split(",")]
for word in words:
    n = int(word, 2)
    if n%5 == 0:
        print "1"
    else:
        print "0"

"""
#----------------------------------------#
Question 12
Level 2

Question:
Write a program, which will find all such numbers between 1000 and 3000 (both included) such that each digit of the number is an even number.
The numbers obtained should be printed in a comma-separated sequence on a single line.

Hints:
In case of input data being supplied to the question, it should be assumed to be a console input.
#----------------------------------------#
"""
for num in range(1000, 3000):
    num_str = str(num)
    is_all_digits_even = True
    for c in num_str:
        c_i = int(c)
        if c_i % 2 != 0:
            is_all_digits_even = False
            break
    if is_all_digits_even:
        print "{} has all even digits".format(num_str)

