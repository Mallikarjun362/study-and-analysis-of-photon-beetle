#!/usr/bin/env python3

# Section 1............... Importing libraries
import random
import copy
from collections import deque
import galois
GF = galois.GF(2**4)
# print(GF.properties)

# ---------------------------------------- PHOTON-256-PERMUTATION ---------------------------------------------
## SBOX LIST
sbox_list = [0xc,5,6,0xb,9,0,0xa,0xd,3,0xe,0xf,8,4,7,1,2]
def list_64_to_8x8_matrix(s) -> list[list[int]]:
    assert len(s) == 64
    m = [[s[i+(j*8)] for j in range(8)] for i in range(8)]
    return m
def matrix_8x8_to_hex_list(m : list[list[int]]):
    lst = []
    for col in range(8):
        for row in range(8):
            lst.append(m[row][col])
    return lst
## 1.ADD-CONSTANT
def add_constant(X : list,k : list):
    new_X = copy.deepcopy(X)
    RC = [1, 3, 7, 14, 13, 11, 6, 12, 9, 2, 5, 10]
    IC = [0, 1, 3, 7, 15, 14, 12, 8]
    for i in range(8):
        new_X[i][0] = new_X[i][0] ^ RC[k] ^ IC[i]
    return new_X
## 2.SUB-CELL
def sub_cell(X):
    new_X = copy.deepcopy(X)
    for i in range(8):
        for j in range(8):
            new_X[i][j] = sbox_list[new_X[i][j]]
    return new_X
## 3.SHIFT-ROW
def shift_row(X):
    new_X = copy.deepcopy(X)
    for i in range(8):
        temp = deque(new_X[i])
        temp.rotate(-1*i)
        new_X[i] = list(temp)
    return new_X
## 4.MIX-COLUMN-SERIAL
def serial(lst):
    M = []
    for i in range(7):
        a = [0 for j in range(8)]
        a[i+1] = 1
        M.append(a)
    M.append(copy.deepcopy(lst))
    return M
def matrix_mul(m1,m2):
    new_m = [[0 for j in range(8)] for i in range(8)]
    for i in range(8):
        for j in range(8):
            s = 0
            for temp in range(8):
                s ^= int(GF(m1[i][temp]) * GF(m2[temp][j]))
            new_m[i][j] = s
    return new_m
def mix_column_serial(X):
    new_X = copy.deepcopy(X)
    M = serial([2, 4, 2, 11, 2, 8, 5, 6])
    M8 = matrix_mul(M,M)
    for i in range(6):
        M8 = matrix_mul(M8,M)
    new_X = matrix_mul(M8,new_X)
    return new_X
## PHOTON 256 PERMUTATION FUNCTION
def PHOTON_256(input_hex_str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"):
    if type(input_hex_str) == "":
        input_hex_str = [int(i,16) for i in input_hex_str]
    assert len(input_hex_str) == 64
    X = list_64_to_8x8_matrix(input_hex_str)
    # 0 to 11
    for i in range(12):
        X = add_constant(X,i)
        X = sub_cell(X)
        X = shift_row(X)
        X = mix_column_serial(X)
    X = matrix_8x8_to_hex_list(X)
    assert len(X) == 64
    return X

## ---------------------------- MATHEMATICAL COMPONENT "RHO" and "RHO_INVERSE" --------------------------------
def shuffel(S):
    r = len(S)
    S1 , S2 = S[:r//2],S[r//2:]
    S1 = [S1[-1]] + S1[:-1]
    return S2 + S1
def list_xor(lst1,lst2):
    return [lst1[i]^lst2[i] for i in range(len(lst1))]
def Ozs(V,r):
    if len(V) < r:
        V.append(1)
        for i in range(r - len(V)):
            V.append(0)
    assert len(V) == r
    return V
def rho(S,U):
    # S = list of bits - State Bits
    # U = list of bits - Message Bits
    # len(U)  <= len(S)
    # mostly len(S)  == len(V) == r
    # input   : (part_r,M)
    # returns : (part_r,C)
    r = len(S)
    V = list_xor(shuffel(S)[:len(U)],U)
    S = list_xor(S,Ozs(U,r))
    return (S,V)
def rho_inverse(S,V):
    # S = list of bits - State Bits
    # V = list of bits - Cipher Bits
    # len(S)  <= len(V)
    # mostly len(S)  == len(V) == r
    r = len(S)
    U = list_xor(shuffel(S)[:len(V)],V)
    S = list_xor(S,Ozs(U,r))
    return (S,U)

#==================================================================================================================================================================
#==================================================================================================================================================================
#==================================================================================================================================================================
# --------------------------------- PHOTON-BEETLE-AEAD-ENCRYPTION --------------------------------------------
def divide_chunks(l, n):
    # looping till length l
    lst = []
    for i in range(0, len(l), n):
        lst.append(l[i:i + n])
    return lst
def bits_list_to_hex_list(lst:list[int]) -> list[int]:
    assert len(lst) % 4 == 0
    new_list = []
    for i in range(len(lst)//4):
        a = int("".join(str(b) for b in lst[i*4:i*4+4]), 2)
        new_list.append(a)
    return new_list

def int_to_bin(a,total_length):
    return list(map(int,format(a, f'0{total_length}b')))
def bits_list_to_str(lst:list[int]) -> list[int]:
    assert len(lst) % 8 == 0
    out_str = ""
    for i in range(len(lst)//8):
        a = chr(int("".join(str(b) for b in lst[i*8:i*8+8]), 2))
        out_str += a
    return out_str
def str_to_bits_list(s:str):
    lst = []
    for i in s:
        lst += int_to_bin(ord(i),8)
    return lst
        

def hex_list_to_bits_list(lst):
    new_list = []
    for i in lst:
        new_list += [int(digit) for digit in '{:04b}'.format(i)]
    return new_list
## --------------------------------------------STEP_1 --------------------------------------------------------
def step_1_sub(IV,A,r,c0=0):
    # IV => list of bits {0,1} - to - list of hex values
    # c0 can be (1,2,3,4)
    assert len(IV) == 256
    # PHOTON
    IV = bits_list_to_hex_list(IV)
    IV = PHOTON_256(IV)
    IV = hex_list_to_bits_list(IV)
    assert len(IV) == 256
    part_r , part_c = IV[:r] , IV[r:]
    assert len(part_r) == len(A)
    # PART-R Transformation
    part_r = list_xor(part_r,A)
    # PART-C Transformation
    if c0 == 0:
        pass
    elif c0 == 1:
        part_c[-1] ^= 1
    elif c0 == 2:
        part_c[-2] ^= 1
    elif c0 == 3:
        part_c[-1] ^= 1
        part_c[-2] ^= 1
    elif c0 == 4:
        part_c[-3] ^= 1
    # Combining
    IV = part_r + part_c
    return IV
def step_1(N,K,A,r,c0):
    assert len(N) + len(K) == 256
    if len(A) == 0:
        return N + K
    else:
        # chunks of length "r"
        A_lst = list(divide_chunks(A,r))
        last_ele = Ozs(A_lst.pop(),r)
        IV = N + K
        for a in A_lst:
            IV = step_1_sub(IV,a,r,0)
        IV = step_1_sub(IV,last_ele,r,c0)
        return IV
## --------------------------------------------STEP_2 --------------------------------------------------------
def step_2_sub(IV,M,r,c1=0):
    assert len(IV) == 256
    # Photon beetle
    IV = bits_list_to_hex_list(IV)
    IV = PHOTON_256(IV)
    IV = hex_list_to_bits_list(IV)
    part_r , part_c = IV[:r] , IV[r:]
    # PART-R Transformation
    part_r,C = rho(part_r,M)
    # PART-C Transformation
    if c1 == 0:
        pass
    elif c1 == 1:
        part_c[-1] ^= 1
    elif c1 == 2:
        part_c[-2] ^= 1
    elif c1 == 5:
        part_c[-1] ^= 1
        part_c[-3] ^= 1
    elif c1 == 6:
        part_c[-2] ^= 1
        part_c[-3] ^= 1
    # Combining
    IV = part_r + part_c
    return (IV,C)
def step_2(IV,M,r,c1):
    if len(M) == 0:
        pass
    else:
        M_lst = list(divide_chunks(M,r))
        last_ele = M_lst.pop()
        C_lst = []
        for m in M_lst:
            IV , temp_c = step_2_sub(IV,m,r,0)
            C_lst += temp_c
        IV , temp_c = step_2_sub(IV,last_ele,r,c1)
        C_lst += temp_c
        
        IV = bits_list_to_hex_list(IV)
        IV = PHOTON_256(IV)
        IV = hex_list_to_bits_list(IV)
        tag = IV[:128]
        
        return (C_lst,tag)
## ----------------------------------------- MAIN INTERFACE-ENCRYPTION ---------------------------------------
# K = bits list , len(k) arbitary
# N = bits list , len(N) arbitary
# len(K) + len(N) == 256
def photon_beetle_enc(K,N,A,M,r=128):
    assert len(K) + len(N) == 256
    
    choice_c0 = {"11" : 1,"10" : 2,"01" : 3,"00" : 4,}
    choice_c1 = {"11" : 1,"10" : 2,"01" : 5,"00" : 6,}
    c0 = choice_c0[f"{int(len(M)>0)}{int(len(A)%r==0)}"]
    c1 = choice_c1[f"{int(len(A)>0)}{int(len(M)%r==0)}"]
    # print(c0,c1)
    
    m_length = len(M)
    IV = step_1(N,K,A,r,c0)
    # print("Step 1 completed")
    C,T = step_2(IV,M,r,c1)
    return [C,T]

#==================================================================================================================================================================
#==================================================================================================================================================================
#==================================================================================================================================================================

## --------------------------------------------STEP_2 --------------------------------------------------------
def step_2_dec_sub(IV,C,r,c1=0):
    #c1 can be (1,2,5,6)
    # returns
    IV = bits_list_to_hex_list(IV)
    IV = PHOTON_256(IV)
    IV = hex_list_to_bits_list(IV)
    part_r , part_c = IV[:r] , IV[r:]
    part_r,M = rho_inverse(part_r,C)
    if c1 == 0:
        pass
    elif c1 == 1:
        part_c[-1] ^= 1
    elif c1 == 2:
        part_c[-2] ^= 1
    elif c1 == 5:
        part_c[-1] ^= 1
        part_c[-3] ^= 1
    elif c1 == 6:
        part_c[-2] ^= 1
        part_c[-3] ^= 1
    IV = part_r + part_c
    return (IV,M)
def step_2_dec(IV,C,r,c1):
    if len(C) == 0:
        pass
    else:
        C_lst = list(divide_chunks(C,r))
        last_ele = C_lst.pop()
        M_lst = []
        for c in C_lst:
            IV , temp_m = step_2_dec_sub(IV,c,r,0)
            M_lst += temp_m
        IV , temp_m = step_2_dec_sub(IV,last_ele,r,c1)
        M_lst += temp_m
        
        IV = bits_list_to_hex_list(IV)
        IV = PHOTON_256(IV)
        IV = hex_list_to_bits_list(IV)
        tag = IV[:128]

        return (M_lst,tag)
## ----------------------------------------- MAIN INTERFACE-DECRYPTION ---------------------------------------
def photon_beetle_dec(K,N,A,C,T,r=128):
    assert len(K) + len(N) == 256
    
    choice_c0 = {"11" : 1,"10" : 2,"01" : 3,"00" : 4,}
    choice_c1 = {"11" : 1,"10" : 2,"01" : 5,"00" : 6,}
    c0 = choice_c0[f"{int(len(C)>0)}{int(len(A)%r==0)}"]
    c1 = choice_c1[f"{int(len(A)>0)}{int(len(C)%r==0)}"]
    # print(c0,c1)
    c_length = len(C)
    # STEP 1 SAME AS ENCRYPTION
    IV = step_1(N,K,A,r,c0)
    # print("Step 1 completed")
    M,new_T = step_2_dec(IV,C,r,c1)
    return [M[:c_length],new_T]

#==================================================================================================================================================================
#==================================================================================================================================================================
#==================================================================================================================================================================