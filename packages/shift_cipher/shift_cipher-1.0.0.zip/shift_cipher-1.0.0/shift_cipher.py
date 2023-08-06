
alphabets = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

#code to encrypt the plain text based upon the key value

def encrypt(plain_txt,key,alpha=alphabets) :
    p_txt = plain_txt.strip().upper()
    plain_list = list(p_txt)
    cipher = []
    for each_item in plain_list :
        plain_index = alpha.index(each_item)
        en = (plain_index + int(key.strip()))%26 
        cipher.append(alpha[en])
    cipher_string = ''.join(cipher)
    return cipher_string

#code to decrypt the cipher text based upon the key value

def decrypt(cipher_txt,key,alpha=alphabets) :
    c_txt = cipher_txt.strip().upper()
    cipher_list = list(c_txt)
    plain = []
    for each_item in cipher_list :
        cipher_index = alpha.index(each_item)
        de = (cipher_index - int(key.strip()))%26
        plain.append(alpha[de])
    plain_string = ''.join(plain)
    return plain_string







        
        
        
    
