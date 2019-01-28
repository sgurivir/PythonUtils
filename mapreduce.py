import sys


# ----------------------------------------------------------
# List comprehension
# ----------------------------------------------------------
def convertToRupee(amount, exchange_rate):
  return float(amount) * exchange_rate

dollar_amounts = [5, 10, 12, 28]

rupee_amounts = [convertToRupee(x, 69) for x in dollar_amounts]
rupee_amounts_alt = list(map(lambda x: convertToRupee(x, 69), dollar_amounts))
print rupee_amounts
print rupee_amounts_alt

# ----------------------------------------------------------
# filter
# ---------------------------------------------------------
tokens = ["aswe", "sfdsasf", "ADEESSSD", "SES", "awessf"]

print filter(lambda x: x.startswith("a"), tokens)
# ---------------
