import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from skimage.metrics import structural_similarity as ssim

def show_difference(original, stego):
    diff = np.abs(original.astype(int) - stego.astype(int))
    diff_gray = np.mean(diff, axis=2)

    diff_gray = diff_gray / diff_gray.max()

    y, x = np.where(diff_gray > 0)
    

    plt.imshow(diff_gray, cmap='gray')
    plt.scatter(x, y, c='blue', s=50)
    plt.title("Pixel Difference Map")
    plt.show()

def show_histogram(original, stego):
    plt.figure(figsize=(10,5))

    plt.subplot(1,2,1)
    plt.hist(original.flatten(), bins=256)
    plt.title("Original Histogram")

    plt.subplot(1,2,2)
    plt.hist(stego.flatten(), bins=256)
    plt.title("Stego Histogram")

    plt.show()

def show_images(original, stego):
    plt.figure(figsize=(10,5))

    plt.subplot(1,2,1)
    plt.imshow(original)
    plt.title("Original")

    plt.subplot(1,2,2)
    plt.imshow(stego)
    plt.title("Stego")

    plt.show()      


def show_heatmap(original, stego):
    diff = np.abs(original.astype(int) - stego.astype(int))
    diff_gray = np.mean(diff, axis=2)

    y1, x1 = np.where(diff_gray > 0)
    y2, x2 = np.where((diff_gray >= 0.05) & (diff_gray < 0.2))
    y3, x3 = np.where((diff_gray >= 0.2) & (diff_gray < 0.4))
    y4, x4 = np.where((diff_gray >= 0.4) & (diff_gray < 0.6))
    y5, x5 = np.where((diff_gray >= 0.6) & (diff_gray < 0.8))


    plt.figure(figsize=(6,6))
    plt.imshow(np.zeros_like(diff_gray), cmap='gray')  # siyah arka plan

    plt.scatter(x1, y1, c="#FFF700", s=50)
    plt.scatter(x2, y2, c="#F3BD1B", s=50)
    plt.scatter(x3, y3, c="#EE8802", s=50)
    plt.scatter(x4, y4, c="#CA2020", s=50)
    plt.scatter(x5, y5, c="#610606", s=50)


    plt.title("Embedding Locations")
    plt.axis('off')
    plt.show()

def compute_ssim(original, stego):
    original = original.astype(float)
    stego = stego.astype(float)
    #print("Farklı piksel sayısı:", np.sum(original != stego))
    score = ssim(original, stego, channel_axis=2, data_range=255)
    #print("{:.10f}".format(score))
    return f"{score:.10f}"