
# import socket
# import threading
# import os

# def receive_messages(sock):
#     while True:
#         msg = sock.recv(1024).decode('utf-8')
#         if msg:
#             print(msg)
#         else:
#             break

# def send_file_to_all(sock, filename):
#     if os.path.isfile(filename):
#         sock.send(f"/sendfile {filename}".encode('utf-8'))
#         sock.send(str(os.path.getsize(filename)).encode('utf-8'))

#         with open(filename, 'rb') as f:
#             bytes_read = f.read(1024)
#             while bytes_read:
#                 sock.send(bytes_read)
#                 bytes_read = f.read(1024)

#         print("文件发送给所有人完成.")
#     else:
#         print("文件不存在!")

# def start_client():
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect(('127.0.0.1', 12345))

#     threading.Thread(target=receive_messages, args=(client,)).start()

#     while True:
#         msg = input()
#         if msg == "/exit":
#             break

#         elif msg.startswith('/sendfile'):
#             _, filename = msg.split()
#             send_file_to_all(client, filename)  # 发送文件给所有用户
#         else:
#             client.send(msg.encode('utf-8'))

#     client.close()

# if __name__ == "__main__":
#     start_client()




import tkinter as tk
from tkinter import simpledialog


import socket
import threading
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

class ChatClient:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.username = None
        
        self.root = tk.Tk()
        self.root.title("聊天客户端")
        
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(pady=10)

        self.msg_entry = tk.Entry(self.root, width=50)
        self.msg_entry.pack(pady=5)

        self.send_button = tk.Button(self.root, text="发送", command=self.send_message)
        self.send_button.pack(pady=5)

        self.file_button = tk.Button(self.root, text="发送文件", command=self.send_file)
        self.file_button.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.request_username()

    def request_username(self):
        username = simpledialog.askstring("用户名", "请输入你的用户名:")
        if username:
            self.username = username
            self.client_socket.send(username.encode('utf-8'))
            threading.Thread(target=self.receive_messages, daemon=True).start()

    def receive_messages(self):
        while True:
            msg = self.client_socket.recv(1024).decode('utf-8')
            if msg:
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, msg + '\n')
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)  # 滚动到底部
            else:
                break

    def send_message(self):
        msg = self.msg_entry.get()
        if msg:
            self.client_socket.send(msg.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)

    def send_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.client_socket.send(f"/sendfile {os.path.basename(filename)}".encode('utf-8'))
            self.client_socket.send(str(os.path.getsize(filename)).encode('utf-8'))

            with open(filename, 'rb') as f:
                bytes_read = f.read(1024)
                while bytes_read:
                    self.client_socket.send(bytes_read)
                    bytes_read = f.read(1024)
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, "文件发送完成.\n")
            self.chat_area.config(state='disabled')

    def on_closing(self):
        self.client_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    ChatClient('127.0.0.1', 12345)
    tk.mainloop()

