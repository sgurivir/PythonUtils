name = [ "Manjeet", "Nikhil", "Shambhavi", "Astha" ] 
roll_no = [ 4, 1, 3, 2 ] 
marks = [ 40, 50, 60, 70 ] 
  
# using zip() to map values 
mapped = zip(name, roll_no, marks) 
  
# converting values to print as list 
mapped = list(mapped) 
  
# printing resultant values  
print (mapped) 
  
print("\n") 
  
# unzipping values 
namz, roll_noz, marksz = zip(*mapped) 

for name, roll, marks in mapped:
  print name, roll, marks
  
print (marksz) 
