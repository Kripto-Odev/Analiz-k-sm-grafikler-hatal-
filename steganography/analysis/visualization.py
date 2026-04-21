import matplotlib.pyplot as plt
import numpy as np
from skimage.metrics import structural_similarity as ssim

def show_difference(original, stego):
    diff = np.abs(original.astype(int) - stego.astype(int))

    plt.imshow(diff)
    plt.title("Pixel Difference Map")
    plt.colorbar()
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
    diff = np.mean(np.abs(original - stego), axis=2)

    plt.imshow(diff, cmap='hot')
    plt.title("Embedding Heatmap")
    plt.colorbar()
    plt.show()
   

def compute_ssim(original, stego):
    return ssim(original, stego, channel_axis=2)