#!/usr/bin/env python3
"""
安全文件写入工具 - 避免 Write 工具常见错误

使用方法:
    python3 scripts/safe_write.py <file_path> <content_file>

或在 Python 中导入:
    from scripts.safe_write import safe_write
    safe_write(file_path, content)
"""

import sys
from pathlib import Path


def safe_write(file_path: str, content: str, chunk_size: int = 50) -> bool:
    """
    安全写入文件，自动处理大文件分块。

    Args:
        file_path: 文件路径（自动转换为绝对路径）
        content: 要写入的内容
        chunk_size: 每块的行数（默认 50 行）

    Returns:
        bool: 写入是否成功
    """
    # 确保使用绝对路径
    path = Path(file_path).resolve()

    # 检查父目录是否存在
    if not path.parent.exists():
        print(f"错误：父目录不存在: {path.parent}")
        return False

    # 分割内容为行
    lines = content.split('\n')
    total_lines = len(lines)

    print(f"准备写入文件: {path}")
    print(f"总行数: {total_lines}")

    # 如果文件较小，直接写入
    if total_lines <= 150:
        try:
            path.write_text(content, encoding='utf-8')
            print(f"✅ 成功写入 {total_lines} 行")
            return True
        except Exception as e:
            print(f"❌ 写入失败: {e}")
            return False

    # 大文件需要分块写入
    print(f"⚠️ 文件较大，将分 {(total_lines + chunk_size - 1) // chunk_size} 块写入")

    try:
        # 第一块：写入前 chunk_size 行
        first_chunk = '\n'.join(lines[:chunk_size])
        path.write_text(first_chunk, encoding='utf-8')
        print(f"✅ 写入第 1 块 ({chunk_size} 行)")

        # 后续块：追加写入
        for i in range(chunk_size, total_lines, chunk_size):
            chunk_lines = lines[i:i + chunk_size]
            chunk_content = '\n' + '\n'.join(chunk_lines)

            with open(path, 'a', encoding='utf-8') as f:
                f.write(chunk_content)

            chunk_num = (i // chunk_size) + 1
            print(f"✅ 追加第 {chunk_num} 块 ({len(chunk_lines)} 行)")

        print(f"✅ 全部写入完成！总计 {total_lines} 行")
        return True

    except Exception as e:
        print(f"❌ 分块写入失败: {e}")
        return False


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("用法: python3 safe_write.py <file_path> <content_file>")
        print("或: echo 'content' | python3 safe_write.py <file_path> -")
        sys.exit(1)

    file_path = sys.argv[1]
    content_source = sys.argv[2]

    # 读取内容
    if content_source == '-':
        content = sys.stdin.read()
    else:
        content_path = Path(content_source)
        if not content_path.exists():
            print(f"错误：内容文件不存在: {content_path}")
            sys.exit(1)
        content = content_path.read_text(encoding='utf-8')

    # 写入文件
    success = safe_write(file_path, content)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
