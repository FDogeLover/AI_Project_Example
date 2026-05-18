# 2025-05-15 deep_learning 项目接入

## 项目基本信息
- 名称: deep_learning
- 类型: ml
- 阶段: 刚开始
- 技术栈: PyTorch + MPS（Mac Apple Silicon）

## 用户提供的信息
- 硬件: Mac（Apple Silicon）
- 方向: 图像（分类、检测、生成）
- 经验: 有实际项目经验

## 设计决策
- 选择 PyTorch（Mac MPS 加速支持最好）
- 预训练 backbone + 迁移学习模式
- 自动检测设备（MPS > CUDA > CPU）

## 后续关注点
- 数据集准备
- 第一个实验的目标
- 是否需要数据增强策略
