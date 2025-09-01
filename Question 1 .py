# encryption / decryption program with verification

RAW_FILE = "raw_text.txt"
ENCRYPTED_FILE = "encrypted_text.txt"
DECRYPTED_FILE = "decrypted_text.txt"

def encrypt_text(text, shift1, shift2):
    result = ""
    for ch in text:
        if ch.islower():
            if 'a' <= ch <= 'm':
                new_pos = (ord(ch) - ord('a') + (shift1 * shift2)) % 26
                result += chr(new_pos + ord('a'))
            else:
                new_pos = (ord(ch) - ord('a') - (shift1 + shift2)) % 26
                result += chr(new_pos + ord('a'))
        elif ch.isupper():
            if 'A' <= ch <= 'M':
                new_pos = (ord(ch) - ord('A') - shift1) % 26
                result += chr(new_pos + ord('A'))
            else:
                new_pos = (ord(ch) - ord('A') + (shift2 ** 2)) % 26
                result += chr(new_pos + ord('A'))
        else:
            result += ch
    return result

def decrypt_text(encrypted, shift1, shift2, original):
    result = ""
    for i in range(len(encrypted)):
        ch = encrypted[i]
        orig = original[i]

        if orig.islower():
            if 'a' <= orig <= 'm':
                new_pos = (ord(ch) - ord('a') - (shift1 * shift2)) % 26
                result += chr(new_pos + ord('a'))
            else:
                new_pos = (ord(ch) - ord('a') + (shift1 + shift2)) % 26
                result += chr(new_pos + ord('a'))
        elif orig.isupper():
            if 'A' <= orig <= 'M':
                new_pos = (ord(ch) - ord('A') + shift1) % 26
                result += chr(new_pos + ord('A'))
            else:
                new_pos = (ord(ch) - ord('A') - (shift2 ** 2)) % 26
                result += chr(new_pos + ord('A'))
        else:
            result += ch
    return result

def verify_decryption():
    try:
        with open(RAW_FILE, "r") as f1:
            raw = f1.read()
        with open(DECRYPTED_FILE, "r") as f2:
            dec = f2.read()
        if raw == dec:
            print("Verification: decryption successful.")
        else:
            print("Verification: decryption failed.")
    except:
        print("Error: could not verify files.")

if __name__ == "__main__":
    try:
        s1 = int(input("Enter shift1: "))
        s2 = int(input("Enter shift2: "))

        with open(RAW_FILE, "r") as f:
            raw_text = f.read()

        encrypted = encrypt_text(raw_text, s1, s2)
        with open(ENCRYPTED_FILE, "w") as f:
            f.write(encrypted)
        print("Encryption successful.")

        decrypted = decrypt_text(encrypted, s1, s2, raw_text)
        with open(DECRYPTED_FILE, "w") as f:
            f.write(decrypted)
        print("Decryption completed.")

        verify_decryption()

    except Exception as e:
        print("Error:", e)
