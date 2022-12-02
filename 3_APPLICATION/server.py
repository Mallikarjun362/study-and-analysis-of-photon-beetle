import socket
import photon_beetle as pb
A_BITS,KN_BITS = None , None
def enc_str(s:str):
    M_bits_lst = pb.str_to_bits_list(s)
    C_bits_lst , T_bits_lst = pb.photon_beetle_enc(KN_BITS[:128],KN_BITS[128:],A_BITS,M_bits_lst,)
    C_assci_str = pb.bits_list_to_str(C_bits_lst)
    T_assci_str = pb.bits_list_to_str(T_bits_lst)
    return [C_assci_str,T_assci_str]
def dec_str(cipher_text:str,tag_str:str):
    C_BITS = pb.str_to_bits_list(cipher_text)
    T_BITS = pb.str_to_bits_list(tag_str)
    M_bits_list , my_T_bits_list = pb.photon_beetle_dec(KN_BITS[:128],KN_BITS[128:],A_BITS,C_BITS,T_BITS)
    M_assci_str = pb.bits_list_to_str(M_bits_list)
    my_T_str = pb.bits_list_to_str(my_T_bits_list)
    if my_T_str == tag_str:
        return M_assci_str
    else:
        return "--NOPE--"


def recv_dec_print(client_socket):
    # RECEIVE FROM SERVER
    data_enc_str,tag = client_socket.recv(1024).decode().split("<-,->")
    data_dec_str = dec_str(data_enc_str,tag)
    print("C:",data_enc_str,"(received)")
    print("C:",data_dec_str)
    print()
    return data_dec_str

def send_enc_print(client_socket):
    msg_to_server = input("-> ")
    if msg_to_server == "":
        msg_to_server = "..."
    msg_to_server_enc,tag = enc_str(msg_to_server)
    final_enc_str = msg_to_server_enc + "<-,->" + tag
    client_socket.send(bytes(f"{final_enc_str}","utf-8"))
    print("->",msg_to_server_enc,"(sent)")
    print()
    return msg_to_server










def server():
    global A_BITS , KN_BITS
    IP = "localhost"
    PORT = 9999  
    server_socket = socket.socket()
    server_socket.bind((IP, PORT)) 
    server_socket.listen(10)
    print("Server Started and Listening to Requests...")
    # SERVER STARTED AND LISTENING FOR CLIENTS
    while True:
        connection , address = server_socket.accept()
        print("Client Connected    :",address)
        # INITIALLY RECEIVES THE NAME OF THE CLIENT
        A_BITS,KN_BITS = connection.recv(1024).decode().split("<-,->") #RECV
        A_BITS = list(map(int,A_BITS))
        KN_BITS = list(map(int,KN_BITS))
        if len(A_BITS)>0:
            #STARTS CHAT
            while True:
                msg_to_client = send_enc_print(connection,)
                if msg_to_client == "BYE":
                    break
                msg_from_client = recv_dec_print(connection)
                if msg_from_client == "BYE":
                    break
        # CLOSES THE CONNECTION
        connection.close()
        print("Client Disconnected :",address)


if __name__ == '__main__':
    server()
# DONE