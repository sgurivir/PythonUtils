import sys
import subprocess

def main(file_name):
  with open(file_name, "r") as f:
    for line in f.readlines():
        for word in line.split(" "):
            print(word)

main("./sample.txt")