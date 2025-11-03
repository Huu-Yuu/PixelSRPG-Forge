# PNG图标合并工具使用说明

## 工具概述

**PNG图标合并工具**（PNG Icon Packer）是一个用于将多个PNG图标合并成单张精灵图（Sprite Sheet）的实用工具。该工具特别适用于游戏开发中需要将多个小图标打包成纹理图集的场景，支持自定义图标尺寸、排列方式，并会自动生成索引文件记录每个图标的位置信息。

## 功能特点

- 自动扫描文件夹中的所有PNG文件
- 支持自定义图标尺寸（可等比例缩放）
- 支持自定义每行图标数量或自动计算最优排列
- 保持原始图标透明度
- 生成详细的索引文件，记录每个图标的位置和尺寸
- 提供直观的命令行界面和友好的交互体验
- 显示处理进度和详细信息

## 安装要求

- Python 3.6 或更高版本
- Pillow 库（用于图像处理）

### 安装依赖

```bash
pip install pillow
```

## 使用方法

### 基本用法

1. 确保已安装所需的依赖（Pillow库）
2. 运行脚本：

```bash
python png_icon_packer.py
```

3. 按照提示输入以下信息：
   - **输入文件夹路径**：包含PNG图标的文件夹路径
   - **输出文件路径**：合并后大图的保存路径（默认为桌面）
   - **图标尺寸**：目标图标尺寸，格式为"宽 高"（默认为24x24）
   - **每行图标数量**：可选，自动计算为近似正方形排列

4. 确认配置后开始处理

### 示例

#### 示例1：基本使用

**操作流程：**
```
请输入包含PNG图标的文件夹路径: C:\Icons\skill_icons
找到 36 个PNG文件
请输入输出文件路径（直接回车将保存到桌面）: C:\Output\skill_iconset.png
请输入图标尺寸（格式：宽 高，如 24 24，直接回车使用默认24x24）: 32 32
请输入每行图标数量（直接回车自动计算）: 6

确认配置信息:
输入文件夹: C:\Icons\skill_icons
输出文件: C:\Output\skill_iconset.png
图标尺寸: 32x32
每行图标: 6

是否开始处理? (y/n): y
```

**处理结果：**
```
开始处理 36 个PNG文件...
目标图标尺寸: 32x32像素
✓ 已完成: attack_icon.png -> 位置(0, 0)
✓ 已完成: defense_icon.png -> 位置(32, 0)
...
✓ 已完成: special_icon.png -> 位置(160, 160)

✓ 大图保存成功: C:\Output\skill_iconset.png
✓ 大图尺寸: 192 x 192 像素
✓ 排列布局: 6 图标/行 × 6 行
✓ 成功处理: 36/36 个图标
✓ 索引文件已生成: C:\Output\skill_iconset_index.txt

🎉 图标合并完成！
```

#### 示例2：使用默认设置

对于快速打包，可以使用大部分默认设置，只需提供输入文件夹：

```
请输入包含PNG图标的文件夹路径: C:\Icons\items
找到 25 个PNG文件
请输入输出文件路径（直接回车将保存到桌面）: [直接回车]
使用默认路径: C:\Users\用户名\Desktop\iconset.png
请输入图标尺寸（格式：宽 高，如 24 24，直接回车使用默认24x24）: [直接回车]
请输入每行图标数量（直接回车自动计算）: [直接回车]

确认配置信息:
输入文件夹: C:\Icons\items
输出文件: C:\Users\用户名\Desktop\iconset.png
图标尺寸: 24x24
每行图标: 自动计算

是否开始处理? (y/n): y
```

## 输出文件说明

### 1. 精灵图文件（.png）

所有图标按照指定的尺寸和排列方式合并成一张大图，背景为透明。

### 2. 索引文件（_index.txt）

自动生成的文本文件，记录了每个原始图标的文件名、在大图中的位置坐标和尺寸信息，格式为：

```
文件名: x坐标,y坐标,宽度,高度
```

示例索引文件内容：

```
# 图标索引文件 - 共36个图标
# 大图尺寸: 192x192
# 图标尺寸: 32x32
# 排列方式: 6图标/行

attack_icon.png: 0,0,32,32
defense_icon.png: 32,0,32,32
heal_icon.png: 64,0,32,32
...
special_icon.png: 160,160,32,32
```

## 游戏开发中的应用

在游戏开发中，您可以使用生成的精灵图和索引文件来：

1. **优化游戏性能**：减少纹理切换次数，提高渲染效率
2. **简化资源管理**：将多个小图标集中管理
3. **实现动画效果**：通过索引文件精确控制显示位置

例如，在代码中访问特定图标：

```python
# 示例：使用索引文件加载特定图标
import pygame
import json

def load_icon_by_name(sheet_path, index_path, icon_name):
    # 加载索引信息
    icon_positions = {}
    with open(index_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                name, coords = line.split(': ')
                x, y, w, h = map(int, coords.split(','))
                icon_positions[name] = (x, y, w, h)
    
    # 加载精灵图
    sheet = pygame.image.load(sheet_path).convert_alpha()
    
    # 获取指定图标的位置和尺寸
    if icon_name in icon_positions:
        x, y, w, h = icon_positions[icon_name]
        # 创建子表面
        icon = pygame.Surface((w, h), pygame.SRCALPHA)
        icon.blit(sheet, (0, 0), (x, y, w, h))
        return icon
    return None
```

## 注意事项

1. 工具会按照文件名排序处理图标，请确保文件名命名合理以获得预期的排列顺序
2. 处理大量或大尺寸图片时，可能需要较多内存，请确保系统资源充足
3. 使用高分辨率图片时，处理时间会相应增加
4. 为保证最佳效果，建议原始图标使用透明背景的PNG格式

## 更新日志

- v1.0：初始版本，支持基本的图标合并和索引生成功能

## 许可证

本工具采用MIT许可证。

---

*本工具是PixelSRPG-Forge项目的一部分，专为像素风格RPG游戏开发设计。*