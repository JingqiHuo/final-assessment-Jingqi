import cv2
import numpy as np
import rasterio
import os

def read_and_preprocess_tiff(tiff_path):
    """读取 TIFF 并转换为 8-bit 图像"""
    if not os.path.exists(tiff_path):
        raise FileNotFoundError(f"⚠️ 文件未找到: {tiff_path}")

    with rasterio.open(tiff_path) as dataset:
        image = dataset.read(1)  # 读取第一波段（假设是 DEM 数据）
    
    # 归一化到 0-255 并转换为 uint8
    image_8bit = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return image_8bit

def connect_nearest_contours(img):
    """连接航线的断点，确保连接最近的端点"""
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

    # 创建一个空白图像，背景为 0，数据点区域为 255
    result_img = np.zeros_like(img)
    result_img[img > 0] = 255  # 保留原始数据线段为 255

    # 连接最近的端点
    for i in range(len(points)):
        min_dist = float("inf")
        best_pair = None

        # 遍历每对端点之间的距离
        for j in range(i + 1, len(points)):
            for pt1 in points[i].values():  # 当前轮廓的所有端点
                for pt2 in points[j].values():  # 另一个轮廓的所有端点
                    dist = np.linalg.norm(np.array(pt1) - np.array(pt2))  # 计算欧几里得距离
                    if dist < min_dist:  # 更新最小距离和最佳端点对
                        min_dist = dist
                        best_pair = (pt1, pt2)

        # 画出最短连接线，并将连接的部分设置为 255
        if best_pair:
            cv2.line(result_img, best_pair[0], best_pair[1], 255, thickness=2)  # 设置为 255

    return result_img

def save_as_tiff(image, output_path, reference_tiff_path):
    """保存图像为 TIFF 格式"""
    with rasterio.open(reference_tiff_path) as dataset:
        # 获取 TIFF 的元数据
        profile = dataset.profile
    
    # 确保输出图像是 uint8 格式
    image = image.astype(np.uint8)

    # 使用 rasterio 写入新的 TIFF 文件
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(image, 1)  # 写入第一个波段

# 🚀 运行
tiff_path = "./task3/2015final.tif"  # 替换为实际路径
img_8bit = read_and_preprocess_tiff(tiff_path)
result_img = connect_nearest_contours(img_8bit)

# 显示最终结果
cv2.imshow("Connected Flight Paths", result_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 保存为 TIFF 文件
output_tiff_path = "./connected_flight_paths.tif"  # 替换为实际路径
save_as_tiff(result_img, output_tiff_path, tiff_path)

print(f"结果已保存至 {output_tiff_path}")


