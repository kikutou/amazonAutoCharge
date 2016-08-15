# coding=utf-8
import time
import random
import os



print time.time()

rno = random.randint(0000000000000000, 9999999999999999)

# f=open("fire.txt","w")

f=open("trade/add/fire.txt", "w")

a = "lw家ぐぇd"

f.write(a)

f.close()

# if not os.path.exists("./trade"):
#     os.mkdir("./trade")
# else:
#     print "no"
#
#
# if not os.path.exists("./trade/"+str(rno)):
#     os.mkdir("./trade/"+str(rno))
# else:
#     print "no"