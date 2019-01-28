
"""
-------- LISTS ----------------------------------------------
"""
list_A = [1,2,3,4,5,6,7,8]
print list_A

# Assign element at index
list_A[0] = 2
print list_A
list_A[0] = 1

# Delete element at index
del list_A[0]
print list_A
list_A.insert(0, 1)
print "After deleting and inserting : {}".format(list_A)

# Delete list
list_B = list_A
del list_B

# Append to a list
list_A.append(9)
print "After Adding 9: {}".format(list_A)

# Slicing a list
print list_A[0:3]

# Delete last three elements of a list
list_B = list_A[:]

list_C = list_B
print list_B
del list_C[-3:-1]  # Notice the order, This also modifies B, as C is copied BY REFERENNCE
print list_B

# Reassign part of list
print "Before reassigning part of list : {}".format(list_A)
list_A[0:1] = [-1, -2]
print list_A

# Heterogeneous items in a list
list_h = ["A", 1, "B", 65, ["A", "B"]]
print list_h
for l in list_h:
    print l

"""
----------------------- Tuples ------------------------------
Tuples are immutable
"""
tuple_t = (1, 2, 3)
print [t for t in tuple_t]

list_k = []
list_k = tuple_t
print tuple_t
print list_k

"""
---------------------- Sets ----------------------------------
Sets don't hold duplicate values.. Hence it is powerful
"""
set_s = {1, 2, 3, 4, 5}
set_s.add(6)
set_s.add(6)
set_s.add(6)
print set_s

"""
-------------------- Dictionaries ----------------------------
"""
dict_d = {"A": 1, "B":2, "C":3, "D":4}
print dict_d["A"]
del dict_d["A"]
print dict_d


"""
------------------------Convert list to set -------------------
"""
list_with_duplicates = [1,2,3,4,5,5,5,6,7,7,8]
set_without_duplicates = set(list_with_duplicates)
print set_without_duplicates
