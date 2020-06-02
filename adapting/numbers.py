#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
numbers.py - Perform stuffs about numbers.
"""

import os, random, re
import reply
from functions import isCalculable
from translated_replies import *

def dec2bin(num):
	if not re.search("^\d+$", num):
		return "nops"
	num=int(num)
	next=num
	bin=[]
	while next != 0:
		bin.append(str(next%2))
		next = int(next) / 2
	bin.reverse()
	bin ="".join(bin) if bin else 0
	return bin

def bin2dec(num):
	if re.search("^[10]+$",num):
		splitted=[]
		for n in num:
			splitted.append(int(n))
		splitted.reverse()
		p=0
		n=0
		for i in splitted:
			n+=i*2**p
			p+=1
		return str(n)

#based on http://code.activestate.com/recipes/81611/
def dec2rom(num):
   """
   Convert an integer to Roman numerals.
   """
   if type(num) == int:
	num=str(num)
   if not re.search("^\d+$", num):
       return
   num = int(num)
   #print "numbers.py num:",type(num), num
   if not 0 < num < 4000:
      return "l'argument ha d'estar entre 1 i 3999" #raise ValueError, "Argument must be between 1 and 3999"   
   ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
   nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
   result = ""
   for i in range(len(ints)):
      count = int(num / ints[i])
      result += nums[i] * count
      num -= ints[i] * count
   return result

def rom2dec(num):
   """
   Convert a roman numeral to an integer.
   """

   if not re.search("[MDCLXVI]+",num, re.I):
      return ""
   num = num.upper()
   nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
   ints = [1000, 500, 100, 50,  10,  5,   1]
   places = []

   for i in range(len(num)):
      c = num[i]
      value = ints[nums.index(c)]
      # If the next place holds a larger number, this value is negative.
      try:
         nextvalue = ints[nums.index(num[i +1])]
         if nextvalue > value:
            value *= -1
      except IndexError:
         # there is no next place.
         pass
      places.append(value)
   sum = 0
   for n in places: sum += n
   # Easiest test for validity...
   if dec2rom(sum) == num:
      return sum
   else:
      return u'les dades no són correctes: %s' % num

def f_calc(self, origin, args):
   params = args.match.group(1)
   if params.count("^")>1: return
   params = params.replace(" ","")
   if isCalculable(params.encode("utf-8")):
      call="echo -e \" scale=30\n"+params.encode('latin-1')+"\"|bc"
      a=os.popen(call)
      lines=a.readlines()
      a.close()
      for i in lines:
         self.msg(origin.target, i)
f_calc.rule = ("^$sign=(.*?)$",)
f_calc.showas = "="

def f_conv(self, origin, args):
   """.conv <numsys> <digit>. """
   conv=args.params.split(" ")
   convtype=conv[0].upper()
   n=0
   if convtype in ["R", "D>R"]:
     n=dec2rom(conv[1])
   elif convtype in ["B", "D>B"]:
     n=dec2bin(conv[1])
   elif convtype=="R>D":
     n=rom2dec(conv[1])
   elif convtype=="B>D":
     n=bin2dec(conv[1])
   if n:
     self.msg(origin.target, args.calluser+n.encode("utf-8"))
f_conv.rule = "conv"
f_conv.showas="conv (D>R|R>D|D>B|B>D)"