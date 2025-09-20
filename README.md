# 照片水印工具 (Photo Watermark Tool)

基于图片EXIF信息的自动日期水印添加工具。从图片的EXIF数据中提取拍摄日期，并在图片上添加可自定义的日期水印。

## 功能特点

- 📸 **自动提取EXIF拍摄日期**：从图片的EXIF信息中读取原始拍摄时间
- 🎨 **自定义水印样式**：支持字体大小、颜色、位置和透明度设置
- 📁 **批量处理**：支持单张图片或整个目录的批量处理
- 💾 **智能输出**：自动创建`原目录名_watermark`子目录保存处理后的图片
- 🔄 **多格式支持**：支持JPEG、PNG、TIFF等常见图片格式
- 🛡️ **安全处理**：原始图片保持不变，处理结果保存到新文件

## 安装依赖

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install Pillow piexif click
```

## 使用方法

### 基本用法

```bash
# 处理单张图片
python main.py "/path/to/photo.jpg"

# 处理整个目录
python main.py "/path/to/photos"
```

### 高级选项

```bash
# 自定义字体大小和颜色
python main.py "/path/to/photos" --font-size 48 --color "#FF0000"

# 设置水印位置
python main.py "/path/to/photos" --position "top_left"

# 设置透明度
python main.py "/path/to/photos" --opacity 0.7

# 使用自定义字体
python main.py "/path/to/photos" --font-path "/path/to/font.ttf"
```

## 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `input_path` | - | - | 输入图片文件路径或目录路径（必需） |
| `--font-size` | `-s` | 36 | 水印字体大小 |
| `--color` | `-c` | #FFFFFF | 水印文字颜色（十六进制格式） |
| `--position` | `-p` | bottom_right | 水印位置 |
| `--font-path` | `-f` | None | 自定义字体文件路径 |
| `--opacity` | `-o` | 1.0 | 水印透明度（0.0-1.0） |

## 支持的水印位置

### 英文位置名称
- `top_left` - 左上角
- `top_center` - 上方居中
- `top_right` - 右上角
- `center_left` - 左侧居中
- `center` - 正中央
- `center_right` - 右侧居中
- `bottom_left` - 左下角
- `bottom_center` - 下方居中
- `bottom_right` - 右下角（默认）

### 中文位置名称
- `左上`、`上中`、`右上`
- `左中`、`居中`、`右中`
- `左下`、`下中`、`右下`

## 项目结构

```
NJUSE25FALL-Photo-Watermark/
├── src/
│   ├── __init__.py
│   ├── exif_reader.py      # EXIF信息读取模块
│   └── watermark_processor.py  # 水印处理模块
├── examples/               # 示例图片目录
├── main.py                # 主程序入口
├── test_app.py            # 测试脚本
├── requirements.txt       # Python依赖
├── .gitignore
└── README.md
```

## 快速测试

运行测试脚本来创建示例图片并验证功能：

```bash
python test_app.py
```

这将会：
1. 创建带有EXIF信息的测试图片（包括PNG格式）
2. 自动运行水印添加功能
3. 在`examples`目录下生成测试结果

## 工作原理

1. **EXIF读取**：程序首先扫描输入路径，找到所有支持的图片文件
2. **日期提取**：从每张图片的EXIF数据中提取`DateTimeOriginal`字段
3. **备选方案**：如果EXIF中没有拍摄日期，则使用文件修改时间
4. **水印绘制**：使用PIL库在指定位置绘制日期文本
5. **文件保存**：将处理后的图片保存到`原目录名_watermark`子目录

## 支持格式

- **输入格式**：JPEG (`.jpg`, `.jpeg`)、PNG (`.png`)、TIFF (`.tiff`, `.tif`)
- **输出格式**：保持与原文件相同的格式
- **EXIF支持**：支持标准EXIF格式的拍摄时间信息（注意：PNG格式通常不包含EXIF信息）

## 注意事项

- 程序会自动创建输出目录，原始图片不会被修改
- PNG格式通常不包含EXIF信息，将使用文件修改时间作为备选
- 如果图片没有EXIF拍摄时间，将使用文件修改时间作为备选
- 水印文件名格式：`原文件名_watermarked.扩展名`
- 建议在处理大量图片前先用小批量测试参数效果

## 开发信息

- **版本**：1.0.0
- **作者**：NJUSE25FALL
- **Python版本要求**：3.7+
- **主要依赖**：PIL/Pillow, piexif

## 许可证

本项目采用MIT许可证，详见LICENSE文件。