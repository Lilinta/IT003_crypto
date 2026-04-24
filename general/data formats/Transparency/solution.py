#!/usr/bin/env python3
"""
Tính SHA-256 fingerprint của public key từ file PEM.

Đây là bước hữu ích để tra cứu Certificate Transparency logs
và tìm chứng chỉ TLS đang dùng đúng public key đó.
"""

import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def main() -> None:
    # Đọc file PEM chứa RSA public key
    with open("transparency.pem", "rb") as f:
        pem_data = f.read()

    # Load public key từ PEM
    public_key = serialization.load_pem_public_key(pem_data)

    # Xuất public key sang DER (SubjectPublicKeyInfo)
    der_bytes = public_key.public_bytes(
        encoding=Encoding.DER,
        format=PublicFormat.SubjectPublicKeyInfo,
    )

    # Tính SHA-256 fingerprint của DER
    fingerprint = hashlib.sha256(der_bytes).hexdigest()

    print("SHA-256 fingerprint:", fingerprint)


if __name__ == "__main__":
    main()