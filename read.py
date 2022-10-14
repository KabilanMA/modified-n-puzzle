with open('first_rest.txt','r') as file1:
    Lines = file1.readlines()

first = []
second = []
for line in Lines:
    first.append(line.split('-')[0].strip())
    second.append(line.split('-')[1].strip())

print('\n'.join(first))
print("SECOND")
print('\n'.join(second))
