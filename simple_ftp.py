import os
import ipaddress
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# hostname = socket.gethostname()
# ip = socket.gethostbyname(hostname)

authorizer = DummyAuthorizer()

while True:
    directory = input("设置用作分享的路径:")
    def check_path(directory):
        return os.path.isdir(directory)
    is_valid = check_path(directory)
    if is_valid:
        os.chdir(directory)
        break
    else:
        print("路径不合法，请重新输入")

admin = input("输入用户名：")

password = input("输入密码：")

authorizer.add_user(admin, password, "./", perm="elradfmwMT")

# authorizer.add_anonymous("./")

handler = FTPHandler

handler.authorizer = authorizer

handler.passive_ports = range(2000,3000)

handler.banner = "OK!" 

# ip = input("请输入本机ip：")

# while True:
#     try:
#         ip_add = ipaddress.ip_address(ip)
#         break
#     except ValueError:
#         ip = input("输入的IP格式有误，请重新输入：")

def port_input(default):
    prompt = "请输入控制端口(默认为21)：".format(default)
    user_input = input(prompt)
    if not user_input:
        return default
    try:
        port = int(user_input)
        if 1 <= port <= 65535:
            return port
        else:
            print("此次输入不是一个有效的端口或不是端口，将以默认端口运行")
            return default
    except ValueError:
        print("此次输入不是一个有效的端口或不是端口，将以默认端口运行")
        return default

control = port_input(21)

print("运行成功，开始启动")

server = FTPServer(("0.0.0.0", control), handler)

server.max_cons = 30  

server.max_cons_per_ip = 5    
 
server.serve_forever()   