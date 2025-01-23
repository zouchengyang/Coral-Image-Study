import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from skimage.draw import line as skimage_line
import tkinter as tk
from tkinter import filedialog
import os
import pandas as pd  

def select_image_file():
    root = tk.Tk()
    root.withdraw()  
    file_path = filedialog.askopenfilename(
        title="选择珊瑚UV照片",
        filetypes=[("图像文件", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
    )
    return file_path

def select_line_points(image):
    plt.imshow(image)
    plt.title("请在图像上点击两点以定义线条")
    points = plt.ginput(2)
    plt.close()
    if len(points) != 2:
        raise ValueError("需要选择两点来定义线条。")
    return int(points[0][0]), int(points[0][1]), int(points[1][0]), int(points[1][1])

def get_line_pixels(x0, y0, x1, y1):
    rr, cc = skimage_line(y0, x0, y1, x1)
    return rr, cc

def extract_rgb_values(image_array, rr, cc):
    rr = np.clip(rr, 0, image_array.shape[0]-1)
    cc = np.clip(cc, 0, image_array.shape[1]-1)
    rgb = image_array[rr, cc]
    return rgb

def plot_rgb_and_ratio(rgb, step_increment='step'):
    steps = np.arange(len(rgb))
    R = rgb[:, 0]
    G = rgb[:, 1]
    B = rgb[:, 2]
    G_B_ratio = G / (B + 1e-6)  

    fig, ax1 = plt.subplots(figsize=(10, 6))

    color_r = 'tab:red'
    color_g = 'tab:green'
    color_b = 'tab:blue'

    ax1.set_xlabel('step')
    ax1.set_ylabel('RGB', color='k')
    ax1.plot(steps, R, color=color_r, label='Red')
    ax1.plot(steps, G, color=color_g, label='Green')
    ax1.plot(steps, B, color=color_b, label='Blue')
    ax1.tick_params(axis='y')
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()  
    color_ratio = 'tab:purple'
    ax2.set_ylabel('G/B ratio', color=color_ratio)
    ax2.plot(steps, G_B_ratio, color=color_ratio, label='G/B Ratio')
    ax2.tick_params(axis='y', labelcolor=color_ratio)
    ax2.legend(loc='upper right')

    plt.title('Changes in RGB Values and G/B Ratio Along the Line')
    fig.tight_layout()
    plt.show()

    return steps, R, G, B, G_B_ratio  

def save_to_csv(steps, R, G, B, G_B_ratio, image_path):
    data = {
        'Step': steps,
        'Red': R,
        'Green': G,
        'Blue': B,
        'G/B Ratio': G_B_ratio
    }
    df = pd.DataFrame(data)

    base_name = os.path.splitext(os.path.basename(image_path))[0]
    csv_filename = f"{base_name}_RGB_GB_Ratio.csv"

    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        initialfile=csv_filename,
        filetypes=[("CSV 文件", "*.csv")],
        title="保存CSV文件"
    )
    if not save_path:
        print("未选择保存位置，数据未保存。")
        return

    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"数据已保存为 {save_path}")

def main():
    image_path = select_image_file()
    if not image_path:
        print("未选择任何文件。程序退出。")
        return

    if not os.path.exists(image_path):
        print(f"无法找到文件: {image_path}")
        return

    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        print(f"无法打开图像: {e}")
        return

    image_array = np.array(img)

    try:
        x0, y0, x1, y1 = select_line_points(image_array)
    except ValueError as ve:
        print(ve)
        return

    rr, cc = get_line_pixels(x0, y0, x1, y1)

    rgb = extract_rgb_values(image_array, rr, cc)

    steps, R, G, B, G_B_ratio = plot_rgb_and_ratio(rgb)

    save_to_csv(steps, R, G, B, G_B_ratio, image_path)

if __name__ == "__main__":
    main()
