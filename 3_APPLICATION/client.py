import socket
# GENERATE Associated-data-bits and KN-bits
# generate 256 bit random key
import subprocess
def int_to_bin(a,total_length):
    return list(map(int,format(a, f'0{total_length}b')))
n_bytes = 256//8
rand_hex_from_openssl = subprocess.run(['openssl', 'rand','-hex',f'{n_bytes}'], stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]
KN_BITS = []
for i in rand_hex_from_openssl:
    KN_BITS += int_to_bin(int(i,16),4)
#DONE
client_IP = "127.0.0.1"
server_IP = "127.0.0.1"
A_BITS = []
for i in (client_IP+"."+server_IP).split("."):
    A_BITS += int_to_bin(int(i),8)
A_data_str = "".join(map(str,A_BITS))
KN_data_str = "".join(map(str,KN_BITS))
#DONE
import photon_beetle as pb
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
#======================================================================================================================================================================
#======================================================================================================================================================================
#======================================================================================================================================================================

def recv_dec_print(client_socket):
    # RECEIVE FROM SERVER
    data_enc_str,tag = client_socket.recv(1024).decode().split("<-,->")
    data_dec_str = dec_str(data_enc_str,tag)
    print("S:",data_enc_str,"(received)")
    print("S:",data_dec_str)
    print()
    return data_dec_str

def send_enc_print(client_socket):
    msg_to_server = input("-> ")
    if msg_to_server == "":
        msg_to_server = "..."
        client_socket.send(bytes(f"{msg_to_server}","utf-8"))
        return msg_to_server
    msg_to_server_enc,tag = enc_str(msg_to_server)
    final_enc_str = msg_to_server_enc + "<-,->" + tag
    client_socket.send(bytes(f"{final_enc_str}","utf-8"))
    print("->",msg_to_server_enc,"(sent)")
    print()
    return msg_to_server




def client():
    global server_IP
    IP = server_IP
    PORT = 9999
    client_socket = socket.socket()
    client_socket.connect((IP, PORT))
    message = A_data_str + "<-,->" + KN_data_str
    # STARTS CONVERSATION BY SENDING USER_NAME
    client_socket.send(message.encode())
    print("Client Started and Successfully Connected to Server...")
    # WAITS FOR REPLY
    while True:
        data = recv_dec_print(client_socket)
        if not data :
            break
        if data == "BYE":
            break
        else:
            msg_to_server = send_enc_print(client_socket)
            if msg_to_server == "BYE":
                break
    client_socket.close()
# STARTING THE CLIENT
client()