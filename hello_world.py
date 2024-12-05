import time
import sys

folder_name = sys.argv[1]
file_name = sys.argv[2]

print(folder_name + " " + file_name)
print()
time.sleep(10)

print("Hello World")

with open(f"output_{folder_name}_{file_name}.txt", "w") as file:
    file.write("Done")
