#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import os
import sys

def svg_to_ico():
    """将SVG图标转换为ICO格式，并生成多种尺寸的图标
    优化版本：添加了缓存检查、内存优化和错误处理
    """
    try:
        # 检查目标文件是否已存在
        icon_path = os.path.join('static', 'app_icon.ico')
        svg_path = os.path.join('static', 'app_icon.svg')

        # 检查目标文件是否已存在且有效
        if os.path.exists(icon_path) and os.path.getsize(icon_path) > 0:
            print(f"Icon file already exists at {icon_path}")
            return icon_path

        # 需要PNG中间格式，因为PIL不能直接读取SVG
        png_path = os.path.join('static', 'app_icon.png')

        if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
            print("ERROR: A PNG version of the icon is required for conversion.")
            print("Please convert your SVG to PNG manually using an image editor")
            print(f"and save it as {png_path}")
            return None

        # 多种尺寸的图标序列
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

        # 使用上下文管理打开文件，确保文件正确关闭
        with Image.open(png_path) as img:
            # 检查图像模式并转换为RGBA模式（如果需要）
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 创建多尺寸图标
            icon_images = []
            for size in sizes:
                try:
                    # 使用高质量的重新调整方法
                    resized_img = img.resize(size, Image.Resampling.LANCZOS)
                    icon_images.append(resized_img)
                except Exception as resize_error:
                    print(f"Warning: Failed to resize to {size}: {resize_error}")
                    # 尝试使用备用方法
                    try:
                        resized_img = img.resize(size, Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
                        icon_images.append(resized_img)
                    except Exception:
                        print(f"Error: Could not resize image to {size}, skipping this size")

            if not icon_images:
                print("Error: Failed to create any icon images")
                return None

            # 保存为ICO格式
            try:
                icon_images[0].save(
                    icon_path,
                    format='ICO',
                    sizes=[(img.width, img.height) for img in icon_images],
                    append_images=icon_images[1:]
                )
                print(f"Icon successfully converted and saved to {icon_path}")
                return icon_path
            except Exception as save_error:
                print(f"Error saving ICO file: {save_error}")
                # 尝试备用方法保存
                try:
                    # 只保存一个尺寸的图标
                    icon_images[0].save(icon_path, format='ICO')
                    print(f"Saved simplified icon to {icon_path}")
                    return icon_path
                except Exception as fallback_error:
                    print(f"Failed to save even simplified icon: {fallback_error}")
                    return None
    except Exception as e:
        print(f"Error converting icon: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数，处理命令行参数并调用图标转换函数"""
    import argparse

    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='Convert PNG icon to ICO format with multiple sizes')
    parser.add_argument('--png', help='Path to PNG file (default: static/app_icon.png)')
    parser.add_argument('--output', help='Output ICO file path (default: static/app_icon.ico)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    # 调用图标转换函数
    result = svg_to_ico()

    # 返回适当的退出代码
    if result:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()