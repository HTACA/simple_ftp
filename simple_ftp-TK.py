import sys
import socket
import threading
import tkinter as tk
from tkinter import *
from tkinter import ttk,filedialog
from hashlib import sha256
from pyftpdlib.authorizers import DummyAuthorizer,AuthenticationFailed
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class DummySHA256Authorizer(DummyAuthorizer):
    def validate_authentication(self, username, password,handler):
        if sys.version_info >= (3,0):
            password = password.encode('latin1')
        hash = sha256(password).hexdigest()
        try:
            if self.user_table[username]['pwd'] != hash:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed
        
class SetupUi(object):
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('ftp')
        self.window.geometry('500x390')
        self.window.minsize(500,390)
        self.window.protocol('WM_DELETE_WINDOW',self.on_closing)

        self.lab1 = Label(self.window,text='主机:',font=('华文行楷',15,'bold'))
        self.lab1.grid(row=0,column=0,padx=(10,0),pady=10)

        # 定义下拉框
        style = ttk.Style()
        style.theme_use('default')
        style.map('TCombobox', fieldbackground=[('selected', 'white')])
        self.lab2 = ttk.Combobox(self.window,state='readonly',font=('华文行楷',15,'bold'),width=16)
        def ip_box():
            def network():
                interfaces = socket.getaddrinfo(socket.gethostname(),None)
                ip_list = []
                for i in interfaces:
                    if ':' not in i[4][0]:
                        ip_list.append(i[4][0])
                return ip_list
            local_address = network()
            return local_address
        self.lab2['value'] = tuple(ip_box())
        self.lab2.current(0)
        self.lab2.grid(row=0,column=1,padx=(5,0),pady=10)

        self.lab3 = Label(self.window,text='端口:',font=('华文行楷',15,'bold'))
        self.lab3.grid(row=0,column=2,padx=(10,0),pady=10)

        self.lineEdit = Entry(self.window,font=('华文行楷',15,'bold'),width=6,validate='key',validatecommand=(self.window.register(self.validate_integer),'%P'))
        self.lineEdit.grid(row=0,column=3,padx=(10,0),pady=10)
        self.lineEdit.insert(0,str(21))

        self.lab4 = Label(self.window,text='账户:',font=('华文行楷',15,'bold'))
        self.lab4.grid(row=1,column=0,padx=(10,0),pady=10)

        self.lineEdit2 = Entry(self.window,font=('华文行楷',15,'bold'),width=16)
        self.lineEdit2.grid(row=1,column=1,padx=(10,0),pady=10)

        self.lab5 = Label(self.window,text='密码:',font=('华文行楷',15,'bold'))
        self.lab5.grid(row=2,column=0,padx=(10,0),pady=10)

        self.lineEdit3 = Entry(self.window,font=('华文行楷',15,'bold'),width=16)
        self.lineEdit3.grid(row=2,column=1,padx=(10,0),pady=10)

        self.path_var = tk.StringVar()
        self.button = tk.Button(self.window,text='选择地址',font=('黑体',10),command=self.selectPath,width=10)
        self.button.grid(row=3,column=0,padx=(10,0),pady=10)

        self.lab6 = Label(self.window,textvariable=self.path_var)
        self.lab6.grid(row=3,column=1,padx=(0,0),pady=10)

        self.button1 = tk.Button(self.window,text='启动',font=('黑体',10),width=10,state='disabled')
        self.button1.grid(row=4,column=0,padx=(10,0),pady=10)

        self.lab7 = Label(self.window)
        self.lab7.grid(row=0,column=4,padx=(10,0),pady=10)
        
        self.bind()
        self.server = None
        self.ftp_thread = None

    def bind(self):
        self.lineEdit.bind('<Leave>',self.port_set)
        self.button1.bind('<Button-1>',self.toggle_server)
        self.lineEdit.bind('<Leave>',self.colose_pushButton)
        self.lineEdit2.bind('<Leave>',self.colose_pushButton)
        self.lineEdit3.bind('<Leave>',self.colose_pushButton)

    def toggle_server(self,event=None):
        if self.server is None:
            self.cure()
        else:
            self.stop_server()

    def stop_server(self):
        if self.server:
            with self.server:
                self.server.close_all()
            self.server = None
            self.ftp_thread = None

            self.lab2.config(state='normal')
            self.lineEdit.config(state='normal')
            self.lineEdit2.config(state='normal')
            self.lineEdit3.config(state='normal')
            self.button.config(state='normal')
            self.button1.config(text='启动')
        
    def validate_integer(self,value):
        if value == '':
            return True
        try:
            int(value)
            return True
        except ValueError:
            return False
 
    def selectPath(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
        return self.path_var.get()
    
    # 监听端口占用状态
    def is_port_open(self):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
            if s.connect_ex((self.lab2.get(),int(self.lineEdit.get()))) == 0:
                self.lab7.config(text='被占用',fg='red')
            else:
                self.lab7.config(text='')
    def port_set(self,event=None):
        self.port_thread = threading.Thread(target=self.is_port_open)
        self.port_thread.start()

    def cure(self):
        authorizer = DummySHA256Authorizer()
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.passive_ports = range(2000,3000)

        host = self.lab2.get()
        port = self.lineEdit.get()
        user = self.lineEdit2.get()
        pwd = sha256(self.lineEdit3.get().encode('latin1')).hexdigest()
        folder = self.lab6.cget('text')

        authorizer.add_user(user,pwd,folder,perm='elradfmwMT')
        self.server = FTPServer((host,port),handler)
        self.server.max_cons = 60
        self.server.max_cons_per_ip = 5
        self.ftp_thread = threading.Thread(target=self.server.serve_forever)
        self.ftp_thread.start()

        self.lab2.config(state='disabled')
        self.lineEdit.config(state='disabled')
        self.lineEdit2.config(state='disabled')
        self.lineEdit3.config(state='disabled')
        self.button.config(state='disabled')
        self.button1.config(text='关闭')
    
    def colose_pushButton(self,*args):     
        if not self.lineEdit.get() or not self.lineEdit2.get() or not self.lineEdit3.get() or self.lab6.cget('text') == '':
            self.button1.config(state='disabled')
            # 窗口焦点控制
            self.window.focus_set()
        else:
            self.button1.config(state='normal')

    def on_closing(self):
        self.stop_server()
        self.window.destroy()

if __name__ == '__main__':
    app = SetupUi()
    app.window.mainloop()
