from django.test import TestCase

# Create your tests here.
a=[["nihao","是的"],["pengyou",32]]
b=[["nihao","是的"],["pengyou",33]]
c=[["nihao","是的"],["pengyou",32]]
dis_list = [
[["nihao","是的"],["pengyou",32]],
[["nihao","是的"],["pengyou",33]],
[["nihao","是的"],["pengyou",32]]
]
for n in range(len(dis_list)-1):
    if (dis_list[n]==dis_list[n+1]):
        flag = 1
        print(flag)
    else:
        break
    print(n)