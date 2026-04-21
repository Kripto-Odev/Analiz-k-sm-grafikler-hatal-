import numpy as np
from core.pvd_utils import get_blocks, difference, quantization

def decode(stego_matrix):
    byte_array = bytearray()
    bit_buffer = ""
    
    # Tüm resmi değil, sadece veriyi bulana kadar tarayacağız
    for coords, p1, p2 in get_blocks(stego_matrix):
        difference_params = difference(p1, p2)
        abs_diff = difference_params[1]
        
        res = quantization(abs_diff)
        if res is None:
            continue
            
        low, high, bit_count = res
        S = max(0, min((high - low), abs_diff - low))
        
        # Gelen sayıyı bitlere çevir ve depoya (buffer) at
        bit_buffer += bin(S)[2:].zfill(int(bit_count))
        
        # Eğer depoda 8 bit (1 byte) veya daha fazlası biriktiyse...
        while len(bit_buffer) >= 8:
            # İlk 8 biti kopar, sayıya çevir ve diziye ekle
            byte_str = bit_buffer[:8]
            byte_array.append(int(byte_str, 2))
            bit_buffer = bit_buffer[8:] # Okunan kısmı sil
            
            # AKILLI ERKEN ÇIKIŞ (EARLY EXIT)
            if len(byte_array) > 4:
                header = byte_array[:4].decode('utf-8', errors='ignore')
                
                if header == "TXT|":
                    # Son 5 byte kontrolü daha temiz ve hatasızdır
                    if len(byte_array) >= 9 and byte_array[-5:] == b"[EOF]":
                        text = byte_array[4:-5].decode('utf-8', errors='ignore')
                        return {"type": "text", "data": text}
                        
                elif header == "IMG|":
                    # ÇÖZÜM: Tüm diziyi tarama, sadece yeni gelen son 5 byte'a bak!
                    if len(byte_array) >= 9 and byte_array[-5:] == b"[EOF]":
                        image_bytes = byte_array[4:-5]
                        return {"type": "image", "data": image_bytes}

    # Eğer resmin en sonuna kadar gelir ve hiçbir şey bulamazsa:
    print("Uyarı: Görüntü sonuna gelindi ancak gizli veri etiketi [EOF] bulunamadı.")
    return {"type": "unknown", "data": byte_array}