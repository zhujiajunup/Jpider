

if __name__ == '__main__':
    a = 1
    b = 2
    while True:
        try:
            c = a/b
            print(c)
            break
        except:
            print('error')
        finally:
            print('finally')
    print('aaaa')