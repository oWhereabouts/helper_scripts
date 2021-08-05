import os

count = 0
input_dir = '/media/unique_tif_folder'

for file in os.listdir(input_dir):
    if file.endswith(".tif"):
        count += 1

print(count)
