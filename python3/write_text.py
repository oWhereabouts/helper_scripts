import os

path = "/home/pking/buildings_names_and_uses/write_text/error.txt"

file1 = open(path,"a")
file1.write("Hello2 \n")
file1.close() #to change file access modes

print("is file {}".format(os.path.isfile(path)))
