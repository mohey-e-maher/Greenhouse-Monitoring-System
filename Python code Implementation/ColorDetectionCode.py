import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

def detect_color(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    low_yellow = np.array([20, 50, 100], dtype=np.uint8)
    high_yellow = np.array([42, 255, 255], dtype=np.uint8)
    mask_yellow = cv2.inRange(hsv, low_yellow, high_yellow)
    
    low_blue = np.array([110, 130, 50], dtype=np.uint8)
    high_blue = np.array([130, 255, 255], dtype=np.uint8)
    mask_blue = cv2.inRange(hsv, low_blue, high_blue)
    
    low_green = np.array([44, 54, 63], dtype=np.uint8)
    high_green = np.array([90, 255, 255], dtype=np.uint8)
    mask_green = cv2.inRange(hsv, low_green, high_green)
    
    cr = cv2.countNonZero(mask_yellow)
    cb = cv2.countNonZero(mask_blue)
    cg = cv2.countNonZero(mask_green)
    
    if cb > 4000:
        return 'Blue'
    elif cg > 32000:
        return 'Green'
    elif cr > 8000:
        return 'Yellow'
    else:
        return 'No Color Detected'

def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        color = detect_color(image)
        result_label.config(text=f"Detected Color: {color}")
        
        # Display image using Matplotlib
        fig = plt.figure(figsize=(6, 4))
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        fig.canvas.manager.window.geometry("+%d+%d" % (root.winfo_x() + root.winfo_width(), root.winfo_y()))
        plt.show()

def quit_application():
    plt.close()
    root.quit()
yellow
root = tk.Tk()
root.title("Color Detection")
root.geometry("400x300")

select_button = tk.Button(root, text="Select Image", command=select_image)
select_button.pack(pady=20)

result_label = tk.Label(root, text="")
result_label.pack()

quit_button = tk.Button(root, text="Quit", command=quit_application)
quit_button.pack(pady=20)

root.mainloop()
