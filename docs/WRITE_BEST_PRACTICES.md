# 避免 Write 工具失败的最佳实践

## 常见错误及解决方案

### 1. 文件内容过大（超过 150 行）

**错误信息：**
```
Write failed: content exceeds line limit
```

**解决方案：**

#### 方法 A：使用 safe_write.py 工具

```bash
# 从文件读取内容并安全写入
python3 scripts/safe_write.py target_file.txt source_content.txt

# 从标准输入写入
echo "content" | python3 scripts/safe_write.py target_file.txt -
```

#### 方法 B：在 Python 代码中使用

```python
from scripts.safe_write import safe_write

content = "很长的内容...\n" * 200
safe_write("output.txt", content)
```

#### 方法 C：手动分块（Claude Code 内部）

```python
# 第一步：写入前 50 行
Write(file_path="file.txt", content=first_50_lines)

# 第二步：追加剩余内容（每次 50 行）
Edit(file_path="file.txt", 
     old_string=last_line_of_previous_chunk,
     new_string=last_line_of_previous_chunk + "\n" + next_50_lines)
```

### 2. 编辑已存在的文件但未先读取

**错误信息：**
```
Write failed: must read file before editing
```

**解决方案：**

```python
# ❌ 错误：直接写入已存在的文件
Write(file_path="existing_file.py", content=new_content)

# ✅ 正确：先读取，再编辑
Read(file_path="existing_file.py")
Edit(file_path="existing_file.py", 
     old_string=old_content,
     new_string=new_content)

# ✅ 或者：如果要完全重写，先读取再写入
Read(file_path="existing_file.py")
Write(file_path="existing_file.py", content=new_content)
```

### 3. 使用相对路径而非绝对路径

**错误信息：**
```
Write failed: path must be absolute
```

**解决方案：**

```python
# ❌ 错误：使用相对路径
Write(file_path="scripts/test.py", content=content)

# ✅ 正确：使用绝对路径
Write(file_path="/home/youfeng/CLionProjects/camera_style/scripts/test.py", 
      content=content)

# ✅ 或者：在 bash 中获取绝对路径
Bash(command="realpath scripts/test.py")
# 然后使用返回的绝对路径
```

### 4. 文件父目录不存在

**错误信息：**
```
Write failed: parent directory does not exist
```

**解决方案：**

```bash
# 先创建目录
mkdir -p /path/to/parent/directory

# 然后写入文件
Write(file_path="/path/to/parent/directory/file.txt", content=content)
```

## 最佳实践总结

### ✅ 推荐做法

1. **新文件**：直接使用 Write
   ```python
   Write(file_path="/absolute/path/new_file.txt", content=content)
   ```

2. **已存在的文件**：先 Read 再 Edit
   ```python
   Read(file_path="/absolute/path/existing_file.txt")
   Edit(file_path="/absolute/path/existing_file.txt",
        old_string="old content",
        new_string="new content")
   ```

3. **大文件（>150 行）**：使用 safe_write.py
   ```python
   from scripts.safe_write import safe_write
   safe_write("/absolute/path/large_file.txt", large_content)
   ```

4. **确保路径正确**：
   ```bash
   # 获取当前工作目录
   pwd
   
   # 获取文件的绝对路径
   realpath relative/path/to/file.txt
   ```

### ❌ 避免的做法

1. ❌ 不要对已存在的文件直接 Write（除非先 Read）
2. ❌ 不要使用相对路径
3. ❌ 不要一次写入超过 150 行（使用分块或 safe_write.py）
4. ❌ 不要在父目录不存在时写入文件

## 快速检查清单

在使用 Write 工具前，检查：

- [ ] 文件路径是绝对路径？
- [ ] 如果文件已存在，是否先用 Read 读取了？
- [ ] 内容是否少于 150 行？（否则使用 safe_write.py）
- [ ] 父目录是否存在？

## 示例：完整工作流

```python
# 场景：创建一个新的大型配置文件

# 1. 确认工作目录
Bash(command="pwd")
# 输出：/home/youfeng/CLionProjects/camera_style

# 2. 准备内容（假设超过 150 行）
large_config = generate_large_config()  # 返回 300 行内容

# 3. 使用 safe_write 工具
from scripts.safe_write import safe_write
safe_write(
    "/home/youfeng/CLionProjects/camera_style/config/large_config.yaml",
    large_config
)

# 4. 验证写入
Bash(command="wc -l config/large_config.yaml")
# 输出：300 config/large_config.yaml
```

## 故障排除

### 问题：Write 总是失败

**诊断步骤：**

```bash
# 1. 检查文件是否存在
ls -la /path/to/file.txt

# 2. 检查父目录权限
ls -ld /path/to/

# 3. 检查磁盘空间
df -h

# 4. 测试写入权限
touch /path/to/test_file.txt && rm /path/to/test_file.txt
```

### 问题：分块写入后文件损坏

**原因：** 可能是编码问题或换行符问题

**解决：**

```python
# 使用 safe_write.py，它会自动处理编码
from scripts.safe_write import safe_write
safe_write(file_path, content)

# 或手动指定编码
with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)
```

## 相关工具

- `scripts/safe_write.py` - 安全文件写入工具
- `Read` - 读取文件内容
- `Edit` - 编辑文件（替换字符串）
- `Write` - 写入新文件或覆盖文件
- `Bash` - 执行 shell 命令

---

**最后更新**: 2026-04-14
