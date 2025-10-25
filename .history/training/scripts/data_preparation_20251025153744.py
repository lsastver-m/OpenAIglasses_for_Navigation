#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据准备脚本
==========

用于准备和预处理训练数据
支持多种数据格式转换和增强

使用方法:
python data_preparation.py --input_dir datasets/raw --output_dir datasets/processed

作者: AI智能眼镜开发团队
版本: v2.4
"""

import os
import json
import cv2
import numpy as np
import argparse
from pathlib import Path
import shutil
from typing import List, Dict, Tuple
import albumentations as A
from albumentations.pytorch import ToTensorV2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

class DataPreparator:
    """数据准备器"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def convert_labelme_to_yolo(self, labelme_file: Path, output_dir: Path):
        """将LabelMe格式转换为YOLO格式"""
        print(f"转换标注文件: {labelme_file}")
        
        with open(labelme_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        img_width = data['imageWidth']
        img_height = data['imageHeight']
        
        yolo_annotations = []
        for shape in data['shapes']:
            if shape['label'] in ['blind_path', 'crosswalk', 'traffic_light', 'obstacle']:
                # 获取类别ID
                class_id = self.get_class_id(shape['label'])
                
                # 转换多边形为边界框
                points = shape['points']
                x_coords = [p[0] for p in points]
                y_coords = [p[1] for p in points]
                
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # 转换为YOLO格式 (归一化坐标)
                x_center = (x_min + x_max) / 2 / img_width
                y_center = (y_min + y_max) / 2 / img_height
                width = (x_max - x_min) / img_width
                height = (y_max - y_min) / img_height
                
                yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
        # 保存YOLO格式标注
        output_file = output_dir / f"{labelme_file.stem}.txt"
        with open(output_file, 'w') as f:
            f.write('\n'.join(yolo_annotations))
        
        return len(yolo_annotations) > 0
    
    def get_class_id(self, label: str) -> int:
        """获取类别ID"""
        class_mapping = {
            'blind_path': 0,
            'crosswalk': 1,
            'traffic_light': 2,
            'obstacle': 3
        }
        return class_mapping.get(label, 0)
    
    def create_augmentation_pipeline(self):
        """创建数据增强管道"""
        return A.Compose([
            A.HorizontalFlip(p=0.5),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.3),
            A.RandomSaturation(saturation_limit=0.2, p=0.3),
            A.RandomShadow(shadow_roi=(0, 0, 1, 1), num_shadows_lower=1, num_shadows_upper=2, p=0.2),
            A.RandomRain(slant_lower=-10, slant_upper=10, drop_length=20, drop_width=1, p=0.1),
            A.RandomSnow(snow_point_lower=0.1, snow_point_upper=0.3, brightness_coeff=2.5, p=0.1),
            A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.3, alpha_coef=0.1, p=0.1),
            A.Rotate(limit=15, p=0.3),
            A.RandomScale(scale_limit=0.2, p=0.3),
            A.RandomCrop(height=640, width=640, p=0.5),
        ])
    
    def augment_data(self, image_path: Path, label_path: Path, output_dir: Path, num_augmentations: int = 5):
        """数据增强"""
        print(f"增强数据: {image_path}")
        
        # 读取图像
        image = cv2.imread(str(image_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 读取标注
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        # 解析YOLO格式标注
        bboxes = []
        class_ids = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) == 5:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # 转换为像素坐标
                img_h, img_w = image.shape[:2]
                x_min = int((x_center - width/2) * img_w)
                y_min = int((y_center - height/2) * img_h)
                x_max = int((x_center + width/2) * img_w)
                y_max = int((y_center + height/2) * img_h)
                
                bboxes.append([x_min, y_min, x_max, y_max])
                class_ids.append(class_id)
        
        # 创建增强管道
        augmentation = self.create_augmentation_pipeline()
        
        # 生成增强数据
        for i in range(num_augmentations):
            try:
                # 应用增强
                augmented = augmentation(image=image, bboxes=bboxes, class_labels=class_ids)
                
                if augmented['image'] is not None and len(augmented['bboxes']) > 0:
                    # 保存增强后的图像
                    aug_image_path = output_dir / f"{image_path.stem}_aug_{i}{image_path.suffix}"
                    cv2.imwrite(str(aug_image_path), cv2.cvtColor(augmented['image'], cv2.COLOR_RGB2BGR))
                    
                    # 转换边界框回YOLO格式
                    aug_h, aug_w = augmented['image'].shape[:2]
                    yolo_lines = []
                    for bbox, class_id in zip(augmented['bboxes'], augmented['class_labels']):
                        x_min, y_min, x_max, y_max = bbox
                        x_center = (x_min + x_max) / 2 / aug_w
                        y_center = (y_min + y_max) / 2 / aug_h
                        width = (x_max - x_min) / aug_w
                        height = (y_max - y_min) / aug_h
                        
                        yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
                    
                    # 保存增强后的标注
                    aug_label_path = output_dir / f"{image_path.stem}_aug_{i}.txt"
                    with open(aug_label_path, 'w') as f:
                        f.write('\n'.join(yolo_lines))
                        
            except Exception as e:
                print(f"增强失败: {e}")
                continue
    
    def split_dataset(self, data_dir: Path, train_ratio: float = 0.7, val_ratio: float = 0.2):
        """划分数据集"""
        print("划分数据集...")
        
        # 获取所有图像文件
        image_files = list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.png"))
        
        # 划分数据集
        train_files, temp_files = train_test_split(image_files, test_size=1-train_ratio, random_state=42)
        val_files, test_files = train_test_split(temp_files, test_size=1-val_ratio/(1-train_ratio), random_state=42)
        
        print(f"训练集: {len(train_files)} 张")
        print(f"验证集: {len(val_files)} 张")
        print(f"测试集: {len(test_files)} 张")
        
        return train_files, val_files, test_files
    
    def create_dataset_structure(self, train_files: List[Path], val_files: List[Path], test_files: List[Path]):
        """创建数据集目录结构"""
        print("创建数据集目录结构...")
        
        # 创建目录
        for split in ['train', 'val', 'test']:
            (self.output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
            (self.output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)
        
        # 复制文件
        for files, split in [(train_files, 'train'), (val_files, 'val'), (test_files, 'test')]:
            for img_file in files:
                # 复制图像
                dst_img = self.output_dir / split / 'images' / img_file.name
                shutil.copy2(img_file, dst_img)
                
                # 复制标注
                label_file = img_file.with_suffix('.txt')
                if label_file.exists():
                    dst_label = self.output_dir / split / 'labels' / label_file.name
                    shutil.copy2(label_file, dst_label)
    
    def create_yaml_config(self, class_names: List[str]):
        """创建YAML配置文件"""
        print("创建YAML配置文件...")
        
        config = {
            'path': str(self.output_dir.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(class_names),
            'names': class_names
        }
        
        yaml_path = self.output_dir / 'dataset.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"配置文件已保存: {yaml_path}")
        return yaml_path
    
    def visualize_dataset(self, data_dir: Path, num_samples: int = 5):
        """可视化数据集"""
        print("可视化数据集...")
        
        # 获取图像文件
        image_files = list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.png"))
        
        # 随机选择样本
        import random
        sample_files = random.sample(image_files, min(num_samples, len(image_files)))
        
        # 创建可视化
        fig, axes = plt.subplots(1, len(sample_files), figsize=(15, 3))
        if len(sample_files) == 1:
            axes = [axes]
        
        for i, img_file in enumerate(sample_files):
            # 读取图像
            image = cv2.imread(str(img_file))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 读取标注
            label_file = img_file.with_suffix('.txt')
            if label_file.exists():
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                # 绘制边界框
                img_h, img_w = image.shape[:2]
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        x_center = float(parts[1])
                        y_center = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        
                        # 转换为像素坐标
                        x_min = int((x_center - width/2) * img_w)
                        y_min = int((y_center - height/2) * img_h)
                        x_max = int((x_center + width/2) * img_w)
                        y_max = int((y_center + height/2) * img_h)
                        
                        # 绘制边界框
                        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
                        cv2.putText(image, f'Class {class_id}', (x_min, y_min-10), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            axes[i].imshow(image)
            axes[i].set_title(f"Sample {i+1}")
            axes[i].axis('off')
        
        plt.tight_layout()
        plt.savefig('dataset_visualization.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("数据集可视化已保存: dataset_visualization.png")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据准备脚本')
    parser.add_argument('--input_dir', type=str, required=True,
                       help='输入数据目录')
    parser.add_argument('--output_dir', type=str, required=True,
                       help='输出数据目录')
    parser.add_argument('--augment', action='store_true',
                       help='是否进行数据增强')
    parser.add_argument('--num_augmentations', type=int, default=5,
                       help='每个样本的增强数量')
    parser.add_argument('--visualize', action='store_true',
                       help='是否可视化数据集')
    
    args = parser.parse_args()
    
    print("🚀 数据准备开始")
    print("=" * 50)
    
    # 创建数据准备器
    preparator = DataPreparator(args.input_dir, args.output_dir)
    
    # 转换标注格式
    input_path = Path(args.input_dir)
    labelme_files = list(input_path.glob("*.json"))
    
    if labelme_files:
        print(f"找到 {len(labelme_files)} 个LabelMe标注文件")
        for labelme_file in labelme_files:
            preparator.convert_labelme_to_yolo(labelme_file, input_path)
    
    # 数据增强
    if args.augment:
        print("开始数据增强...")
        image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
        for img_file in image_files:
            label_file = img_file.with_suffix('.txt')
            if label_file.exists():
                preparator.augment_data(img_file, label_file, input_path, args.num_augmentations)
    
    # 划分数据集
    train_files, val_files, test_files = preparator.split_dataset(input_path)
    
    # 创建数据集结构
    preparator.create_dataset_structure(train_files, val_files, test_files)
    
    # 创建YAML配置
    class_names = ['blind_path', 'crosswalk', 'traffic_light', 'obstacle']
    yaml_path = preparator.create_yaml_config(class_names)
    
    # 可视化数据集
    if args.visualize:
        preparator.visualize_dataset(input_path)
    
    print("\n🎉 数据准备完成!")
    print(f"   输出目录: {args.output_dir}")
    print(f"   配置文件: {yaml_path}")

if __name__ == "__main__":
    main()
