def chinese_remainder_theorem(a_list, n_list):
    """
    Giải hệ phương trình đồng dư bậc nhất bằng Chinese Remainder Theorem.
    :param a_list: Mảng chứa các số dư (remainders)
    :param n_list: Mảng chứa các modulo (phải nguyên tố cùng nhau từng đôi một)
    """
    # Bước 1: Tính tích của tất cả các modulo (N)
    N = 1
    for n in n_list:
        N *= n
        
    result = 0
    
    # Bước 2 & 3 & 4: Tính toán cho từng phương trình
    for a, n in zip(a_list, n_list):
        Ni = N // n
        
        # Tìm nghịch đảo modulo của Ni trong modulo n. 
        # pow(cơ_số, -1, mod) là cách xịn nhất trong Python 3.8+ để tính nghịch đảo.
        Mi = pow(Ni, -1, n)
        
        # Cộng dồn vào kết quả
        result += a * Ni * Mi
        
    # Trả về kết quả nhỏ nhất trong khoảng từ 0 đến N-1
    return result % N

# ==========================================
# ÁP DỤNG VÀO BÀI CRYPTOHACK CỦA BẠN
# ==========================================

# x ≡ 2 mod 5
# x ≡ 3 mod 11
# x ≡ 5 mod 17
remainders = [2, 3, 5]
moduli = [5, 11, 17]

flag = chinese_remainder_theorem(remainders, moduli)
print(f"Giá trị của a (cờ) là: {flag}")