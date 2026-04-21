import numpy as np
import math

def psnr(original, stego):
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(mse))


def bit_error_rate(original_bits, extracted_bits):
    length = min(len(original_bits), len(extracted_bits))
    errors = sum(1 for i in range(length) if original_bits[i] != extracted_bits[i])
    return errors / length if length > 0 else 0

def mse(original, stego):
    return np.mean((original.astype(float) - stego.astype(float)) ** 2)


def verify_payload(original_data, decoded_data):
    if original_data == decoded_data:
        return True
    return False

def capacity_usage(matrix, message_bits):
    max_capacity = matrix.size * 3
    return len(message_bits) / max_capacity


def analyze_security(original_matrix, stego_matrix, original_bits, decoded_bits):
    results = {}

    results["MSE"] = mse(original_matrix, stego_matrix)
    results["PSNR"] = psnr(original_matrix, stego_matrix)
    results["BER"] = bit_error_rate(original_bits, decoded_bits)
    results["Payload Integrity"] = verify_payload(original_bits, decoded_bits)

    return results