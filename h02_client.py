import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 5012  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    # s.sendall(b"*HQ,865205030330012,V1,145452,A,2240.55181,N,11358.32389,E,0.00,0,100815,FFFFFBFF#")
    # s.sendall(b"*HQ,865205030330012,V2,150421,A,2240.55841,N,11358.33462,E,2.06,0,100815,FFFFFBFF#")
    s.sendall(bytes.fromhex("2410307310010503162209022212874500113466574c014028fffffbffff0001"))
    # wrong Y format s.sendall(bytes.fromhex("5906410400001533281008152240563200113583509e003000e7e7fbffff0009"))
