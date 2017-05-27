import ConfigParser


cf = ConfigParser.ConfigParser()
cf.read(r'.\info.conf')
sections = cf.sections()
username = cf.get('user', 'username')
password = cf.get('user', 'password')
goods = '|'.join(cf.get('user', 'goods').split(' '))
print username, password, goods
