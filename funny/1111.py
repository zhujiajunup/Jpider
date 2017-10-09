import itertools


def is_perfect(input_str):
    found = False
    for index in range(len(input_str)-3):
        if not found:
            if input_str[index] == input_str[index+1]:
                if input_str[index+2] == input_str[index+3]:
                    found = True
                else:
                    return False
        else:
            if input_str[index] == input_str[index+1]:
                return False
    else:
        return found

s = input()
all_perm = set()
for i in itertools.permutations(s, len(s)):
    print(i)
    all_perm.add(''.join(list(i)))
count = 0
for i in all_perm:
    if is_perfect(i):
        print(i)
        count += 1
print(count)
