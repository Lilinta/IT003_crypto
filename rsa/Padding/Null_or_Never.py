# Các thông số đề bài cho
n = 95341235345618011251857577682324351171197688101180707030749869409235726634345899397258784261937590128088284421816891826202978052640992678267974129629670862991769812330793126662251062120518795878693122854189330426777286315442926939843468730196970939951374889986320771714519309125434348512571864406646232154103
e = 3
c = 63476139027102349822147098087901756023488558030079225358836870725611623045683759473454129221778690683914555720975250395929721681009556415292257804239149809875424000027362678341633901036035522299395660255954384685936351041718040558055860508481512479599089561391846007771856837130233678763953257086620228436828

# Thay thế bytes_to_long: int.from_bytes(data, 'big')
# Thay thế long_to_bytes: x.to_bytes((x.bit_length() + 7) // 8, 'big')

for i in range(33, 93):
    PR.<x> = PolynomialRing(Zmod(n))
    
    prefix = b'crypto{'
    # Tạo padding tương tự như logic cũ
    m_bytes = prefix + (b'\x00' * i) + b'}' + (b'\x00' * (100 - len(prefix) - i - 1))
    
    # Chuyển bytes sang số nguyên (thay cho bytes_to_long)
    m = int.from_bytes(m_bytes, 'big')
    
    # Thiết lập đa thức
    shift = 256**(100 - len(prefix) - i)
    f = (m + shift * x)^e - c
    f = f.monic()
    
    # Tìm nghiệm nhỏ (Coppersmith Method)
    roots = f.small_roots(epsilon=1/30)
    
    if roots:
        root_val = int(roots[0])
        # Chuyển số nguyên sang bytes (thay cho long_to_bytes)
        middle = root_val.to_bytes((root_val.bit_length() + 7) // 8, 'big')
        
        try:
            full_flag = (prefix + middle + b'}').decode()
            print(f"Found: {full_flag}")
        except:
            print(f"Found root but could not decode: {middle}")
        break
    else:
        print(f'Checking length {i}: Not yet!!!')