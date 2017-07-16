
def get_account():
    accounts = []
    conf_file = 'conf/account.conf'
    try:
        with open(conf_file, 'r') as f:
            for line in f.readlines():
                fields = line.split(' ')
                accounts.append({'username': fields[0], 'password': fields[1]})
    except FileNotFoundError:
        raise FileNotFoundError('No such file or directory:%s,'
                                ' read conf/README to conf weibo account' % conf_file)
    return accounts