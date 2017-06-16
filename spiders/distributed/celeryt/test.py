from tasks import add, sub

add_rs = add.delay(1, 2)
sub_rs = sub.delay(3, 1)
print add_rs.get()
print sub_rs.get()
