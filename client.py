import socket
import threading
import os

def receive_messages(sock):
    while True:
        msg = sock.recv(1024).decode('utf-8')
        if msg:
            print(msg)
        else:
            break

def send_file(sock, filename):
    if os.path.isfile(filename):
        sock.send(f"/sendfile {filename}".encode('utf-8'))
        sock.send(str(os.path.getsize(filename)).encode('utf-8'))

        with open(filename, 'rb') as f:
            bytes_read = f.read(1024)
            while bytes_read:
                sock.send(bytes_read)
                bytes_read = f.read(1024)
        print("文件发送完成.")
    else:
        print("文件不存在!")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 12345))
    
    threading.Thread(target=receive_messages, args=(client,)).start()

    while True:
        msg = input()
        if msg == "/exit":
            break
        
        if msg.startswith('/call'):
            client.send(msg.encode('utf-8'))
        elif msg.startswith('/group'):
            client.send(msg.encode('utf-8'))
        elif msg.startswith('/sendfile'):
            _, filename = msg.split()
            send_file(client, filename)
        else:
            client.send(msg.encode('utf-8'))

    client.close()

if __name__ == "__main__":
    start_client()
