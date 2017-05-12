to = open('./funny_comment#', 'w')
with open('./funny_comment') as f:
    for line in f.readlines():
        to.write('#'+line)
to.close()