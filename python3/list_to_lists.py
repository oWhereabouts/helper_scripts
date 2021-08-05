import math

lst = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    0,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
]

sublist_size = 5
group_size = 12

sublists = []
for i in range(0, len(lst), sublist_size):
    sublists.append(lst[i : i + sublist_size])

# print(sublists)

lists_per_group = group_size / sublist_size
print(lists_per_group)
if not lists_per_group.is_integer():
    lists_per_group = int(math.ceil(lists_per_group))

print(lists_per_group)

grouped_lists = []
for i in range(0, len(sublists), lists_per_group):
    grouped_lists.append(sublists[i : i + lists_per_group])

print(grouped_lists)
