from PIL import Image
import numpy as np
import os
import math

#pvd tablosu
range_table=[(0,7),(8,15),(16,31),(32, 63), (64, 127), (128, 255)]

def load_image_as_matrix(image_path):
    try:
        image=Image.open(image_path)
        if image.format != 'PNG':
            raise ValueError(f"Hata: Seçilen dosya {image.format} formatında. Sadece PNG desteklenmektedir.")

        image_rgb=image.convert('RGB')
        pixel_matrix=np.array(image_rgb) # numpy matrisine dönüştürme

        print(f"Görüntü başarıyla yüklendi: {image_rgb.size[0]}x{image_rgb.size[1]} boyutunda.")
        return pixel_matrix
    except Exception as e:
        print(f"hata: {e}")
        return None

def get_blocks(matrix):
    shape = matrix.shape
    height = shape[0]
    width=shape[1]
    channels=shape[2]

    # her satırı tek tek gez
    for y in range(height):
        for x in range(0, width-1, 2): #pvd için 1x2 bloklar. width-1: genişlik tek sayıysa son pikselin dışarıda kalması için
            for c in range(channels):
                coordinats=(y,x,c)
                p1=int(matrix[y, x, c]) #pi
                p2=int(matrix[y, x+1, c]) #pi+1

                yield coordinats,p1,p2 # blok işlendikçe her bloğu tek tek döndürür

def difference(p1,p2):
    diff=p1-p2
    abs_diff=abs(diff) #bloğun pürüzsüz mü kenar mı olduğunu anlamak için
    return diff,abs_diff

def quantization(abs_diff): #kapasite
    for low,high in range_table:
        if low<=abs_diff<=high:
            width=high-low+1

            #kaç bit gizleneceği: n = log2(genişlik)
            bit_count=math.log(width,2)

            return low,high,bit_count
    return None