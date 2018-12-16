

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

"""
Question 13
Level 2

Question:
Write a program that accepts a sentence and calculate the number of letters and digits.
Suppose the following input is supplied to the program:
hello world! 123
Then, the output should be:
LETTERS 10
DIGITS 3
"""
line = "A 1 Quick Brown fox jumped over 10 lazy dogs"
counts = {"LETTERS": 0, "DIGITS": 3}
for c in line:
    if c.isdigit():
        counts["DIGITS"] += 1
    if c.isalpha():
        counts["LETTERS"] += 1

print counts["DIGITS"]
print counts["LETTERS"]


"""
Question 15
Level 2

Question:
Write a program that computes the value of a+aa+aaa+aaaa with a given digit as the value of a.
Suppose the following input is supplied to the program:
9
Then, the output should be:
11106
"""
input_digit = "9"
a1 = int("{}".format(input_digit))
a2 = int("{}{}".format(input_digit, input_digit))
a3 = int("{}{}{}".format(input_digit, input_digit, input_digit))
a4 = int("{}{}{}{}".format(input_digit, input_digit, input_digit, input_digit))
print a1 + a2 + a3 + a4

"""
Question 16
Level 2

Question:
Use a list comprehension to square each odd number in a list. The list is input by a sequence of comma-separated numbers.
Suppose the following input is supplied to the program:
1,2,3,4,5,6,7,8,9
Then, the output should be:
1,3,5,7,9
"""

original_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
filtered_list = [x for x in original_list if x % 2 == 1]
print filtered_list

"""
Question 17
Level 2

Question:
Write a program that computes the net amount of a bank account based a transaction log from console input. The transaction log format is shown as following:
D 100
W 200

D means deposit while W means withdrawal.
Suppose the following input is supplied to the program:
D 300
D 300
W 200
D 100
Then, the output should be:
500
"""
transactions = ["D 300",
                "D 300",
                "W 200",
                "D 100",
                "D 500"
               ]
deposits = list(filter(lambda _x : _x.startswith("D"), transactions))
deposits = [int(x.replace("D ", "")) for x in deposits]

withdrawals = list(filter(lambda _x : _x.startswith("W"), transactions))
withdrawals = [int(x.replace("W ", "")) for x in withdrawals]

balance = 0
print deposits
print withdrawals
print sum(deposits) - sum(withdrawals)

"""
Sets examples
Sets dont hold duplicates.. You can create set by using its constructor (or) using {}
"""
set_x = set(["A", "B", "C"])
set_x.add("D")
set_x.add("A")
print set_x

set_y = {"A", "B", "C"}
set_y.add("D")
set_y.add("A")
print set_y



"""
#----------------------------------------#
Question 19
Level 3

Question:
You are required to write a program to sort the (name, age, height) tuples by ascending order where name is string, age and height are numbers. The tuples are input by console. The sort criteria is:
1: Sort based on name;
2: Then sort based on age;
3: Then sort by score.
The priority is that name > age > score.
If the following tuples are given as input to the program:
Tom,19,80
John,20,90
Jony,17,91
Jony,17,93
Json,21,85
Then, the output of the program should be:
[('John', '20', '90'), ('Jony', '17', '91'), ('Jony', '17', '93'), ('Json', '21', '85'), ('Tom', '19', '80')]
"""

students = [("Tom", 19, 80),
            ("John", 20, 20),
            ("Jony", 17, 91),
            ("jony", 17, 93),
            ("Json", 21, 85)
            ]


"""
def get_student(s_):
    for student in s_:
        student(0) = student(0).upper()
        yield student


from operator import itemgetter
print sorted(get_student(students), key=itemgetter(0,1,2))
"""

"""
#----------------------------------------#
Question 20
Level 3

Question:
Define a class with a generator which can iterate the numbers, which are divisible by 7, between a given range 0 and n.

Hints:
Consider use yield
"""
