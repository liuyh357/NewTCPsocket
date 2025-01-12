


import socket
import threading
import os

clients = {}
usernames = {}
groups = {}
call_requests = {}
active_calls = {}




# def handle_client(client_socket):
#     client_socket.send("请输入你的用户名:".encode('utf-8'))
#     username = client_socket.recv(1024).decode('utf-8')
#     clients[client_socket] = username
#     usernames[username] = client_socket
#     broadcast(f"{username} 已上线", None)
#     send_user_list()

#     while True:
#         try:
#             msg = client_socket.recv(1024).decode('utf-8')
#             if msg.startswith('/call'):
#                 _, target_username = msg.split()
#                 threading.Thread(target=call_user, args=(client_socket, target_username)).start()
#             elif msg.startswith('/accept'):
#                 if client_socket in call_requests:
#                     target_socket = call_requests[client_socket]
#                     if target_socket:
#                         active_calls[client_socket] = target_socket
#                         active_calls[target_socket] = client_socket
#                         target_socket.send(f"{clients[client_socket]} 接受了通话请求.".encode('utf-8'))
#                         del call_requests[client_socket]
#                 else:
#                     client_socket.send("没有通话请求.".encode('utf-8'))
#             elif msg.startswith('/endcall'):
#                 handle_end_call(client_socket)
#             elif msg.startswith('/group'):
#                 _, group_name = msg.split()
#                 join_group(client_socket, username, group_name)
#             elif msg.startswith('/sendfile'):
#                 _, filename = msg.split()
#                 receive_file(client_socket, filename)
#                 request_file_transfer(client_socket, filename)
#             elif client_socket in active_calls:  # Check if the client is in an active call
#                 # Handle direct chat during a call
#                 target_socket = active_calls[client_socket]
#                 target_socket.send(f"{username} (通话): {msg}".encode('utf-8'))
#             else:
#                 broadcast(f"{username}: {msg}", client_socket)
#         except Exception as e:
#             print(e)
#             break

#     client_socket.close()
#     del clients[client_socket]
#     del usernames[username]
#     broadcast(f"{username} 已下线", None)
#     send_user_list()


def handle_client(client_socket):
    while True:
        client_socket.send("请输入你的用户名:".encode('utf-8'))
        username = client_socket.recv(1024).decode('utf-8')
        
        # 检查用户名是否已经存在
        if username in usernames:
            client_socket.send("用户名已存在，请选择一个不同的用户名!".encode('utf-8'))
        else:
            break  # 用户名可用，退出循环

    clients[client_socket] = username
    usernames[username] = client_socket
    broadcast(f"{username} 已上线", None)
    send_user_list()

    while True:
        try:
            msg = client_socket.recv(1024).decode('utf-8')
            if msg.startswith('/call'):
                _, target_username = msg.split()
                threading.Thread(target=call_user, args=(client_socket, target_username)).start()
            elif msg.startswith('/accept'):
                if client_socket in call_requests:
                    target_socket = call_requests[client_socket]
                    if target_socket:
                        active_calls[client_socket] = target_socket
                        active_calls[target_socket] = client_socket
                        target_socket.send(f"{clients[client_socket]} 接受了通话请求.".encode('utf-8'))
                        del call_requests[client_socket]
                else:
                    client_socket.send("没有通话请求.".encode('utf-8'))
            elif msg.startswith('/endcall'):
                handle_end_call(client_socket)
            elif msg.startswith('/group'):
                _, group_name = msg.split()
                join_group(client_socket, username, group_name)
            elif msg.startswith('/sendfile'):
                _, filename = msg.split()
                receive_file(client_socket, filename)
                request_file_transfer(client_socket, filename)
            elif client_socket in active_calls:  # Check if the client is in an active call
                # Handle direct chat during a call
                target_socket = active_calls[client_socket]
                target_socket.send(f"{username} (通话): {msg}".encode('utf-8'))
            else:
                broadcast(f"{username}: {msg}", client_socket)
        except Exception as e:
            print(e)
            break

    client_socket.close()
    del clients[client_socket]
    del usernames[username]
    broadcast(f"{username} 已下线", None)
    send_user_list()


def send_user_list():
    user_list = "当前在线用户: " + ', '.join(usernames.keys())
    for client in clients:
        client.send(user_list.encode('utf-8'))

def broadcast(msg, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(msg.encode('utf-8'))

def call_user(caller_socket, target_username):
    if target_username in usernames:
        target_socket = usernames[target_username]
        target_socket.send(f"{clients[caller_socket]} 想要与你通话，接受请回复 /accept".encode('utf-8'))
        call_requests[target_socket] = caller_socket  # Store the call request
    else:
        caller_socket.send("用户不在线.".encode('utf-8'))

def join_group(client_socket, username, group_name):
    if group_name not in groups:
        groups[group_name] = []
    groups[group_name].append(client_socket)
    client_socket.send(f"已加入群组 {group_name}".encode('utf-8'))
    for member in groups[group_name]:
        member.send(f"{username} 已加入群组 {group_name}".encode('utf-8'))

def receive_file(client_socket, filename):
    file_size = client_socket.recv(1024).decode('utf-8')
    file_size = int(file_size)

    with open(f"received_{filename}", 'wb') as f:
        bytes_received = 0
        while bytes_received < file_size:
            bytes_data = client_socket.recv(1024)
            f.write(bytes_data)
            bytes_received += len(bytes_data)

    broadcast(f"文件 {filename} 已发送给群组或用户", client_socket)

def request_file_transfer(sender_socket, filename):
    target_username = sender_socket.recv(1024).decode('utf-8')
    if target_username in usernames:
        target_socket = usernames[target_username]
        target_socket.send(f"{clients[sender_socket]} 想要发送文件: {filename}. 你想下载吗？请输入 /download 或 /reject".encode('utf-8'))
        # 等待接收用户的响应
        response = target_socket.recv(1024).decode('utf-8')
        if response == '/download':
            send_file(sender_socket, target_socket, filename)
        elif response == '/reject':
            target_socket.send("文件传输被拒绝.".encode('utf-8'))
    else:
        sender_socket.send("用户不在线.".encode('utf-8'))

def send_file(sender_socket, target_socket, filename):
    if os.path.isfile(filename):
        target_socket.send(f"开始接收文件 {filename}, 大小: {os.path.getsize(filename)} bytes".encode('utf-8'))
        target_socket.send(str(os.path.getsize(filename)).encode('utf-8'))
        with open(filename, 'rb') as f:
            bytes_read = f.read(1024)
            while bytes_read:
                target_socket.send(bytes_read)
                bytes_read = f.read(1024)
        sender_socket.send("文件发送完成.".encode('utf-8'))
    else:
        sender_socket.send("文件不存在。".encode('utf-8'))

def handle_end_call(client_socket):
    if client_socket in active_calls:
        target_socket = active_calls[client_socket]
        target_socket.send(f"{clients[client_socket]} 结束了通话.".encode('utf-8'))

        # Remove the call from both sides
        del active_calls[client_socket]
        del active_calls[target_socket]

        client_socket.send("通话已结束.".encode('utf-8'))
    else:
        client_socket.send("你当前没有在通话中.".encode('utf-8'))

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))
    server.listen(5)
    print("服务器启动，监听端口 12345")

    while True:
        client_socket, addr = server.accept()
        print(f"连接来自 {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    start_server()
