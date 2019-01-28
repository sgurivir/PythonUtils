import sys
import subprocess

line = raw_input("Enter line : ")
words = line.split(" ")
if len(words) > 9:
  del words[9]
line = " ".join(words)
print line
