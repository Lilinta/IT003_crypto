import cv2

# 1. Đọc 2 bức ảnh bị mã hóa từ đề bài
# Lưu ý: Thay đổi tên file cho khớp với file bạn tải về
img_lemur = cv2.imread('lemur.png')
img_flag = cv2.imread('flag.png')

# Kiểm tra xem ảnh có được load thành công không
if img_lemur is None or img_flag is None:
    print("Error! Not Found. Please check the address!")
else:
    # 2. Thực hiện phép XOR trực tiếp giữa 2 bức ảnh
    # Phép toán này sẽ tự động XOR từng pixel RGB tương ứng của 2 ảnh
    result_img = cv2.bitwise_xor(img_lemur, img_flag)

    # 3. Lưu bức ảnh kết quả ra máy
    cv2.imwrite('decrypted_flag.png', result_img)
    print("[*] Open file ""decrypted_flag.png"" and check by eye.")