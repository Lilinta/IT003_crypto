def matrix2bytes(matrix):
    """
    Chuyển ma trận 4x4 về chuỗi 16 byte.
    Ma trận lưu theo row-major nên chỉ cần flatten theo hàng.
    """
    return bytes(sum(matrix, []))


state = [
    [206, 243, 61, 34],
    [171, 11, 93, 31],
    [16, 200, 91, 108],
    [150, 3, 194, 51],
]

round_key = [
    [173, 129, 68, 82],
    [223, 100, 38, 109],
    [32, 189, 53, 8],
    [253, 48, 187, 78],
]


def add_round_key(s, k):
    """
    Thực hiện XOR từng phần tử của state với round key.
    """
    result = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(s[i][j] ^ k[i][j])
        result.append(row)
    return result


# Thực hiện AddRoundKey
new_state = add_round_key(state, round_key)

# In flag
print(matrix2bytes(new_state).decode())
