import os
import shutil
from PIL import Image
import math
import traceback

def get_user_input():
    """
    获取用户输入的配置参数
    """
    print("=" * 50)
    print("          PNG图标处理工具")
    print("=" * 50)
    print("1. 仅复制PNG文件")
    print("2. 仅合并PNG文件")
    print("3. 先复制后合并")
    print("=" * 50)
    
    # 获取功能选择
    while True:
        choice_input = input("请选择功能 (1/2/3，默认3): ").strip()
        if not choice_input:
            function_choice = 3
            break
        try:
            function_choice = int(choice_input)
            if function_choice in [1, 2, 3]:
                break
            else:
                print("请输入1、2或3")
        except ValueError:
            print("请输入有效的数字")
    
    # 获取输入文件夹路径
    while True:
        input_folder = input("请输入包含PNG图标的文件夹路径: ").strip().strip('"')
        
        # 移除路径两端的引号（如果用户拖拽文件夹进来可能会带引号）
        input_folder = input_folder.strip('"').strip("'")
        
        if not input_folder:
            print("路径不能为空，请重新输入。")
            continue
            
        if not os.path.exists(input_folder):
            print(f"错误：路径 '{input_folder}' 不存在，请重新输入。")
            continue
            
        # 此时只检查路径是否有效，不检查PNG文件数量（会在后面根据递归选项处理）
        break
    
    # 获取是否递归查找的选项
    while True:
        recursive_input = input("是否递归查找子目录中的PNG文件？(y/n，默认y): ").strip().lower()
        if not recursive_input:
            recursive = True
            break
        elif recursive_input in ['y', 'yes', '是', '1']:
            recursive = True
            break
        elif recursive_input in ['n', 'no', '否', '0']:
            recursive = False
            break
        else:
            print("输入格式错误，请输入 y 或 n")
    
    # 根据功能选择确定是否需要复制文件和合并文件
    copy_files = function_choice in [1, 3]
    merge_files = function_choice in [2, 3]
    
    # 如果需要复制文件，获取输出目录
    output_dir = None
    if copy_files:
        while True:
            # 默认输出目录为源目录下的output文件夹
            default_output_dir = os.path.join(input_folder, "output")
            output_dir_input = input(f"请输入输出目录路径（直接回车使用默认: {default_output_dir}）: ").strip().strip('"')
            
            if not output_dir_input:
                output_dir = default_output_dir
                break
            else:
                output_dir = output_dir_input.strip('"').strip("'")
                # 检查父目录是否存在
                parent_dir = os.path.dirname(output_dir)
                if parent_dir and not os.path.exists(parent_dir):
                    print(f"错误：父目录 '{parent_dir}' 不存在，请重新输入。")
                    continue
                break
    
    # 如果需要合并文件，获取合并相关参数
    output_file = None
    icon_size = (24, 24)
    max_per_row = None
    if merge_files:
        # 获取输出文件路径
        output_file = input("请输入输出文件路径（直接回车将保存到桌面）: ").strip().strip('"')
        if not output_file:
            # 默认保存到桌面
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            output_file = os.path.join(desktop, "iconset.png")
            print(f"使用默认路径: {output_file}")
        else:
            output_file = output_file.strip('"').strip("'")
            # 确保文件扩展名是.png
            if not output_file.lower().endswith('.png'):
                output_file += '.png'
        
        # 获取是否使用原尺寸
        while True:
            use_original_size_input = input("是否使用PNG原尺寸合并？(y/n，默认n): ").strip().lower()
            if not use_original_size_input:
                use_original_size = False
                break
            elif use_original_size_input in ['y', 'yes', '是', '1']:
                use_original_size = True
                break
            elif use_original_size_input in ['n', 'no', '否', '0']:
                use_original_size = False
                break
            else:
                print("输入格式错误，请输入 y 或 n")
        
        # 如果不使用原尺寸，则获取目标图标尺寸
        icon_size = None
        if not use_original_size:
            while True:
                size_input = input("请输入图标尺寸（格式：宽 高，如 24 24，直接回车使用默认24x24）: ").strip()
                if not size_input:
                    icon_size = (24, 24)
                    break
                
                try:
                    width, height = map(int, size_input.split())
                    if width <= 0 or height <= 0:
                        print("尺寸必须为正整数，请重新输入。")
                        continue
                    icon_size = (width, height)
                    break
                except ValueError:
                    print("输入格式错误，请使用'宽 高'的格式，如：24 24")
        
        # 获取每行图标数量
        while True:
            row_input = input("请输入每行图标数量（直接回车自动计算）: ").strip()
            if not row_input:
                max_per_row = None
                break
            
            try:
                max_per_row = int(row_input)
                if max_per_row <= 0:
                    print("每行图标数量必须为正整数，请重新输入。")
                    continue
                break
            except ValueError:
                print("请输入有效的数字。")
    
    return input_folder, output_file, icon_size, max_per_row, recursive, copy_files, output_dir, merge_files, function_choice, use_original_size

def find_all_png_files(root_folder):
    """
    递归查找指定文件夹及其所有子目录中的PNG文件
    
    参数说明:
        root_folder: 要搜索的根文件夹路径
    
    返回:
        list: 找到的所有PNG文件的绝对路径列表
    """
    png_files = []
    
    try:
        for dirpath, dirnames, filenames in os.walk(root_folder):
            for filename in filenames:
                if filename.lower().endswith('.png'):
                    png_path = os.path.join(dirpath, filename)
                    png_files.append(png_path)
    except Exception as e:
        print(f"遍历文件夹时出错: {str(e)}")
    
    return png_files

def is_valid_png(file_path):
    """
    检查PNG文件是否可以正常打开
    
    参数说明:
        file_path: PNG文件路径
    
    返回:
        bool: 是否为有效的PNG文件
    """
    try:
        with Image.open(file_path) as img:
            # 尝试加载图像数据
            img.verify()
            return True
    except Exception:
        return False

def copy_valid_png_files(png_files, output_dir):
    """
    将有效的PNG文件复制到指定目录
    
    参数说明:
        png_files: 有效PNG文件的路径列表
        output_dir: 目标输出目录
    
    返回:
        tuple: (成功复制的文件数, 失败的文件数)
    """
    # 创建输出目录（如果不存在）
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n已创建输出目录: {output_dir}")
    except Exception as e:
        print(f"创建输出目录失败: {str(e)}")
        return 0, len(png_files)
    
    success_count = 0
    fail_count = 0
    
    print(f"\n开始复制文件到 {output_dir}...")
    
    # 用于处理文件名冲突
    filename_counter = {}
    
    for file_path in png_files:
        try:
            # 获取原始文件名
            original_filename = os.path.basename(file_path)
            
            # 检查文件名冲突，如果存在则添加序号
            if original_filename in filename_counter:
                filename_counter[original_filename] += 1
                name, ext = os.path.splitext(original_filename)
                new_filename = f"{name}_{filename_counter[original_filename]}{ext}"
            else:
                filename_counter[original_filename] = 0
                new_filename = original_filename
            
            # 目标路径
            dest_path = os.path.join(output_dir, new_filename)
            
            # 复制文件
            shutil.copy2(file_path, dest_path)
            success_count += 1
            
            # 显示进度
            if success_count % 10 == 0 or success_count == len(png_files):
                print(f"已复制: {success_count}/{len(png_files)} 个文件")
                
        except Exception as e:
            print(f"✗ 复制失败: {file_path} - 错误: {str(e)}")
            fail_count += 1
    
    return success_count, fail_count

def process_png_files(input_folder, recursive=True):
    """
    处理PNG文件的通用函数，扫描并验证PNG文件
    
    参数说明:
        input_folder: 包含PNG图标的源文件夹路径
        recursive: 是否递归查找子目录中的PNG文件
    
    返回:
        tuple: (valid_png_files, invalid_png_files)
    """
    # 根据是否递归选择查找方式
    if recursive:
        print(f"正在递归查找 {input_folder} 及其所有子目录中的PNG文件...")
        # 递归查找所有PNG文件
        all_png_files = find_all_png_files(input_folder)
    else:
        print(f"正在查找 {input_folder} 中的PNG文件（不包括子目录）...")
        # 只查找当前目录的PNG文件
        try:
            all_png_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) 
                           if os.path.isfile(os.path.join(input_folder, f)) and f.lower().endswith('.png')]
        except Exception as e:
            print(f"读取文件夹时出错: {str(e)}")
            return [], []
    
    # 筛选出可正常打开的PNG文件
    valid_png_files = []
    invalid_png_files = []
    
    for png_file in all_png_files:
        if is_valid_png(png_file):
            valid_png_files.append(png_file)
        else:
            invalid_png_files.append(png_file)
    
    # 打印无法打开的PNG文件
    if invalid_png_files:
        print(f"\n无法打开的PNG文件 ({len(invalid_png_files)} 个):")
        for invalid_file in invalid_png_files[:10]:  # 只显示前10个
            print(f"  - {invalid_file}")
        if len(invalid_png_files) > 10:
            print(f"  - ...等{len(invalid_png_files) - 10}个文件")
    
    # 按路径排序有效的PNG文件
    valid_png_files.sort()
    total_icons = len(valid_png_files)
    
    # 根据递归选项显示不同的错误信息
    if total_icons == 0:
        if recursive:
            print("\n错误：指定文件夹及其子目录中未找到可打开的PNG文件！")
        else:
            print("\n错误：指定文件夹中未找到可打开的PNG文件！")
        return [], invalid_png_files
    
    # 显示统计信息
    if recursive:
        print(f"\n在 {input_folder} 及其子目录中找到:")
    else:
        print(f"\n在 {input_folder} 中找到:")
    print(f"  - 可处理的PNG文件: {total_icons} 个")
    print(f"  - 无法打开的PNG文件: {len(invalid_png_files)} 个")
    
    return valid_png_files, invalid_png_files

def pack_icons(valid_png_files, output_path, icon_size=(24, 24), max_icons_per_row=None, use_original_size=False):
    """
    将PNG图标合并成一张精灵图（sprite sheet）
    
    参数说明:
        valid_png_files: 有效的PNG文件路径列表
        output_path: 合并后大图的输出保存路径
        icon_size: 每个图标的目标尺寸（当use_original_size=False时使用），默认为24x24像素
        max_icons_per_row: 大图中每行最多排列的图标数量，None表示自动计算
        use_original_size: 是否使用PNG原尺寸进行合并，默认为False
    """
    total_icons = len(valid_png_files)
    
    print(f"\n开始处理 {total_icons} 个PNG文件...")
    if use_original_size:
        print("使用PNG原尺寸合并")
    else:
        print(f"目标图标尺寸: {icon_size[0]}x{icon_size[1]}像素")

    # 计算大图的布局尺寸
    if max_icons_per_row is None:
        # 自动计算近似正方形的排列方式
        max_icons_per_row = math.ceil(math.sqrt(total_icons))
    
    num_rows = math.ceil(total_icons / max_icons_per_row)
    
    # 初始大图尺寸计算
    if use_original_size:
        # 使用原尺寸时，先创建一个临时的小尺寸图
        # 后面会重新计算并创建合适大小的大图
        sheet = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
    else:
        # 使用指定尺寸时的常规计算
        sheet_width = max_icons_per_row * icon_size[0]
        sheet_height = num_rows * icon_size[1]
        sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    # 记录每个图标的位置信息
    index_info = []

    # 处理每个图标文件
    success_count = 0
    for index, img_path in enumerate(valid_png_files):
        try:
            # 获取文件名（不含路径）
            filename = os.path.basename(img_path)
            
            # 打开并处理图片
            with Image.open(img_path) as img:
                # 确保图片模式为RGBA（支持透明度）
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 根据是否使用原尺寸决定是否缩放
                if use_original_size:
                    # 使用原尺寸
                    current_icon_size = img.size
                    img_resized = img
                else:
                    # 高质量缩放图片到指定尺寸
                    current_icon_size = icon_size
                    img_resized = img.resize(icon_size, Image.Resampling.LANCZOS)
                
                # 计算图标在大图中的坐标位置
                row = index // max_icons_per_row
                col = index % max_icons_per_row
                x = col * current_icon_size[0]
                y = row * current_icon_size[1]
                
                # 将处理后的图标粘贴到大图上
                sheet.paste(img_resized, (x, y))
                
                # 保存位置信息供后续使用
                index_info.append({
                    'filename': filename,
                    'full_path': img_path,
                    'x': x,
                    'y': y,
                    'width': current_icon_size[0],
                    'height': current_icon_size[1]
                })
                
                success_count += 1
                print(f"✓ 已完成: {filename} -> 位置({x}, {y})")
                
        except Exception as e:
            print(f"✗ 处理失败: {filename} - 错误: {str(e)}")
            # 打印详细错误信息便于调试
            # print(traceback.format_exc())
            continue

    # 如果使用原尺寸，需要重新创建适当大小的大图
    if use_original_size and success_count > 0:
        # 计算每个图标的实际位置和大图所需尺寸
        # 先计算每行每列的最大尺寸
        row_heights = []
        col_widths = []
        
        # 初始化行列尺寸列表
        for i in range(num_rows):
            row_heights.append(0)
        for i in range(max_icons_per_row):
            col_widths.append(0)
        
        # 计算每行每列的最大尺寸
        for info in index_info:
            row = info['y'] // info['height']
            col = info['x'] // info['width']
            if row < len(row_heights):
                row_heights[row] = max(row_heights[row], info['height'])
            if col < len(col_widths):
                col_widths[col] = max(col_widths[col], info['width'])
        
        # 计算大图尺寸
        total_width = sum(col_widths)
        total_height = sum(row_heights)
        
        # 创建新的大图
        new_sheet = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        
        # 重新排列图标到新的大图中
        current_y = 0
        for row_idx in range(num_rows):
            current_x = 0
            for col_idx in range(max_icons_per_row):
                # 找到对应的图标信息
                icon_idx = row_idx * max_icons_per_row + col_idx
                if icon_idx < len(index_info):
                    info = index_info[icon_idx]
                    # 打开原图
                    with Image.open(info['full_path']) as img:
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        # 粘贴到新位置
                        new_sheet.paste(img, (current_x, current_y))
                        # 更新图标信息中的坐标
                        info['x'] = current_x
                        info['y'] = current_y
                current_x += col_widths[col_idx]
            current_y += row_heights[row_idx]
        
        # 更新sheet引用和尺寸
        sheet = new_sheet
        sheet_width = total_width
        sheet_height = total_height
    
    # 保存合并后的大图
    try:
        sheet.save(output_path, 'PNG')
        print(f"\n✓ 大图保存成功: {output_path}")
        print(f"✓ 大图尺寸: {sheet_width} x {sheet_height} 像素")
        print(f"✓ 排列布局: {max_icons_per_row} 图标/行 × {num_rows} 行")
        print(f"✓ 成功处理: {success_count}/{total_icons} 个图标")
    except Exception as e:
        print(f"✗ 保存大图失败: {str(e)}")
        return False

    # 生成图标位置索引文件
    try:
        index_path = os.path.splitext(output_path)[0] + '_index.txt'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(f"# 图标索引文件 - 共{success_count}个图标\n")
            f.write(f"# 大图尺寸: {sheet_width}x{sheet_height}\n")
            # 避免访问可能为None的icon_size
            if use_original_size:
                f.write(f"# 图标尺寸: 原尺寸\n")
            else:
                f.write(f"# 图标尺寸: {icon_size[0]}x{icon_size[1]}\n")
            f.write(f"# 排列方式: {max_icons_per_row}图标/行\n\n")
            
            for info in index_info:
                # 写入文件名和位置信息
                f.write(f"{info['filename']}: {info['x']},{info['y']},{info['width']},{info['height']}\n")
            
            # 在文件末尾添加完整路径信息
            f.write(f"\n# 完整文件路径信息\n")
            for info in index_info:
                f.write(f"# {info['filename']}: {info['full_path']}\n")
        
        print(f"✓ 索引文件已生成: {index_path}")
    except Exception as e:
        print(f"✗ 生成索引文件失败: {str(e)}")

    return True

def main():
    """
    主函数：处理用户交互和程序流程
    """
    try:
        # 获取用户配置
        input_folder, output_file, icon_size, max_per_row, recursive, copy_files, output_dir, merge_files, function_choice, use_original_size = get_user_input()
        
        # 确认信息
        print(f"\n确认配置信息:")
        print(f"功能选择: {function_choice} - {'先复制后合并' if function_choice == 3 else '仅复制PNG文件' if function_choice == 1 else '仅合并PNG文件'}")
        print(f"输入文件夹: {input_folder}")
        print(f"递归查找: {'是' if recursive else '否'}")
        
        # 根据功能选择显示不同的确认信息
        if copy_files:
            print(f"复制文件: 是")
            print(f"目标目录: {output_dir}")
        
        if merge_files:
            print(f"合并文件: 是")
            print(f"输出文件: {output_file}")
            print(f"使用原尺寸: {'是' if use_original_size else '否'}")
            if not use_original_size:
                print(f"图标尺寸: {icon_size[0]}x{icon_size[1]}")
            print(f"每行图标: {max_per_row or '自动计算'}")
        
        confirm = input("\n是否开始处理? (y/n): ").strip().lower()
        if confirm not in ['y', 'yes', '是']:
            print("操作已取消。")
            return
        
        # 首先扫描并验证PNG文件
        valid_png_files, invalid_png_files = process_png_files(input_folder, recursive)
        total_icons = len(valid_png_files)
        
        # 如果没有有效PNG文件，无法继续处理
        if total_icons == 0:
            print("错误: 找不到有效的PNG文件，无法继续处理。")
            return
        
        # 执行复制文件操作（如果需要）
        success_copy = False
        copied_files = []
        if copy_files:
            success_copy, fail_copy = copy_valid_png_files(valid_png_files, output_dir)
            print(f"\n文件复制结果:")
            print(f"  - 成功复制: {success_copy} 个文件")
            print(f"  - 复制失败: {fail_copy} 个文件")
            
            # 如果是先复制后合并的模式，将合并的源目录改为复制后的目录
            if function_choice == 3:
                # 获取复制后的文件路径列表
                # 创建一个文件名映射，处理可能的命名冲突
                filename_map = {}
                copied_files = []
                for file_path in valid_png_files:
                    original_filename = os.path.basename(file_path)
                    if original_filename in filename_map:
                        filename_map[original_filename] += 1
                        name, ext = os.path.splitext(original_filename)
                        new_filename = f"{name}_{filename_map[original_filename]}{ext}"
                    else:
                        filename_map[original_filename] = 0
                        new_filename = original_filename
                    # 检查文件是否存在
                    copied_file_path = os.path.join(output_dir, new_filename)
                    if os.path.exists(copied_file_path):
                        copied_files.append(copied_file_path)
                
                print(f"\n已找到 {len(copied_files)} 个复制后的有效PNG文件，将用于合并操作")
        
        # 执行合并文件操作（如果需要）
        success_merge = False
        if merge_files:
            print("\n开始合并图标...")
            # 如果是先复制后合并模式，使用复制后的文件；否则使用原始的有效文件
            files_to_merge = copied_files if (function_choice == 3 and copied_files) else valid_png_files
            success_merge = pack_icons(files_to_merge, output_file, icon_size, max_per_row, use_original_size)
        
        # 显示最终结果
        print("\n" + "=" * 50)
        print("处理完成!")
        print("=" * 50)
        
        if copy_files:
            print(f"复制功能: {'成功' if success_copy else '失败'}")
        
        if merge_files:
            print(f"合并功能: {'成功' if success_merge else '失败'}")
            
    except KeyboardInterrupt:
        print("\n\n操作被用户中断。")
    except Exception as e:
        print(f"\n程序运行出错: {str(e)}")
        print("详细错误信息:")
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")

if __name__ == "__main__":
    main()