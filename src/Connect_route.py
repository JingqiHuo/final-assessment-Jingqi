import cv2
import numpy as np
import rasterio
from rasterio.transform import from_origin
import os

def read_and_preprocess_tiff(tiff_path):
    """ 读取 TIFF 并转换为 8-bit 图像 """
    if not os.path.exists(tiff_path):
        raise FileNotFoundError(f"⚠️ 文件未找到: {tiff_path}")

    with rasterio.open(tiff_path) as dataset:
        image = dataset.read(1)  # 读取第一波段（假设是 DEM 数据）
    
    # 归一化到 0-255 并转换为 uint8
    image_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return image_8bit

def connect_nearest_contours(img):
    """ 连接航线的断点 """
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)  # 转换为彩色以便绘制线条

    # 二值化
    _, th = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

    # 形态学膨胀，增强航线
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
    morph = cv2.morphologyEx(th, cv2.MORPH_DILATE, kernel)

    # 轮廓检测
    cnts, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遍历所有轮廓，计算极端点
    points = []
    for c in cnts:
        left = tuple(c[c[:, :, 0].argmin()][0])
        right = tuple(c[c[:, :, 0].argmax()][0])
        top = tuple(c[c[:, :, 1].argmin()][0])
        bottom = tuple(c[c[:, :, 1].argmax()][0])
        points.append({"left": left, "right": right, "top": top, "bottom": bottom})

    # 获取线条的粗细（假设通过形态学膨胀的二值化图像来近似）
    line_thickness = 1  # 默认粗细为1
    non_zero_pixels = np.count_nonzero(morph)  # 计算非零像素数量
    total_pixels = morph.size  # 总像素数

    if non_zero_pixels / total_pixels > 0.05:  # 如果二值化图像的非零像素比例较大
        line_thickness = 30  # 设置较粗的线条

    # 连接最近的端点
    for i in range(len(points)):
        min_dist = float("inf")
        best_pair = None

        for j in range(i + 1, len(points)):
            for pt1 in points[i].values():
                for pt2 in points[j].values():
                    dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
                    if dist < min_dist:
                        min_dist = dist
                        best_pair = (pt1, pt2)

        # 画出最短连接线
        if best_pair:
            cv2.line(img_color, best_pair[0], best_pair[1], (255, 255, 255), thickness=line_thickness)

    # Convert back to grayscale (single channel) for saving as TIFF
    img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

    return img_gray

def save_as_tiff(image, output_path, reference_tiff_path):
    """ 保存图像为 TIFF 格式 """
    with rasterio.open(reference_tiff_path) as dataset:
        # 获取 TIFF 的元数据
        profile = dataset.profile
    
    # 确保输出图像是 uint8 格式
    image = image.astype(np.uint8)

    # 使用 rasterio 写入新的 TIFF 文件
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(image, 1)  # 写入第一个波段


















