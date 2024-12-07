#以下代码实现：将指定目录下所有的.html文件转换为.pdf文件格式；并合并成一个pdf文件。

import os
import pdfkit
from PyPDF2 import PdfMerger

# 指定目录
directory = 'D:/api'

# 初始化PDF合并器
merger = PdfMerger()

# 配置wkhtmltopdf的路径
path_wkthmltopdf = r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'      #安装：https://wkhtmltopdf.org/downloads.html
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)

# 遍历指定目录下的所有.html文件
for filename in os.listdir(directory):
    if filename.endswith('.html'):
        # 使用pdfkit将.html文件转换为.pdf文件
        pdfkit.from_file(os.path.join(directory, filename), os.path.join(directory, filename + '.pdf'), configuration=config, options={'encoding': 'utf-8',"enable-local-file-access":True})
        # 将转换后的.pdf文件添加到PDF合并器中
        merger.append(os.path.join(directory, filename + '.pdf'))

# 将所有.pdf文件合并为一个.pdf文件并保存在同一目录下
merger.write(os.path.join(directory, 'merged.pdf'))
merger.close()

