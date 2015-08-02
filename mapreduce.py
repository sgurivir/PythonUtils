import sys

def convertDollarToRupees(dollarAmount) :
  return dollarAmount * 63
  
def simpleMapExample():
  dollar_amounts = [ 10, 20, 30, 40, 50, 60 ]
  print map(convertDollarToRupees, dollar_amounts)

def lambdaExample():
  dollar_amounts = [ 10, 20, 30, 40, 50, 60 ]
  print map(lambda x:x*63, dollar_amounts)
  
def lambdaCircumferenceAndArea():
  boxes = [[1,2], [3,4], [5,6] , [4,4]]
  print map(lambda x: (x[0]*x[1], x[0]+x[1]), boxes)
  
def reduceSimpleExample():
  scores = [ 47, 53, 102, 98, 2, 20, 8, 70 ]
  print reduce( lambda x,y: x+y, scores)
  
def main():
  simpleMapExample()
  simpleMapInlineExample()
  lambdaExample()
  lambdaCircumferenceAndArea()
  reduceSimpleExample()

main()
  
