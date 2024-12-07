import pydoc
import importlib
import os

def get_package_help_info(package_name):
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        print(f"Error: Package '{package_name}' not found.")
        return

    with open(f'{package_name}_help.txt', 'w', newline='', encoding='utf-8-sig') as f:
        for name in dir(package):
            obj = getattr(package, name)
            if callable(obj) or hasattr(obj, '__module__'):
                try:
                    help_content = pydoc.render_doc(obj)
                    f.write(f"Help for {name}:\n{help_content}\n\n")
                except Exception as e:
                    print(f"Error rendering help for {name}: {e}")

# 示例用法：获取vectorbt库中的帮助信息
package_name = 'vectorbt'
get_package_help_info(package_name)
print(f"Help information for package '{package_name}' has been written to '{package_name}_help.txt'.")





import vectorbt
import pydoc    # 生成Python模块的文档

class_names = [vectorbt.utils, vectorbt.data, vectorbt.generic, vectorbt.indicators, vectorbt.signals, vectorbt.records, vectorbt.portfolio, vectorbt.labels]

with open('vectorbt_class_help.txt', 'w', newline='', encoding='utf-8-sig') as f:
    for class_name in class_names:
        help_content = pydoc.render_doc(class_name)
        f.write(f"Help for {class_name.__name__}:\n{help_content}\n\n")
# 把以上代码改写成函数：get_package_help—_info(package_name)
# 1. 自动分析package_name库中包含的所有类，函数
# 2. 输出package_name库中包含的所有类，函数的帮助信息到文件
# 3. 文件名的格式为：package_name + "_help.txt"

import vectorbt
import pydoc

class_names = [vectorbt.utils, vectorbt.data, vectorbt.generic, vectorbt.indicators, vectorbt.signals, vectorbt.records, vectorbt.portfolio, vectorbt.labels]

with open('vectorbt_class_help.txt', 'w', encoding='utf-8') as f:
    for class_name in class_names:
        help_content = pydoc.render_doc(class_name)
        f.write(f"Help for {class_name.__name__}:\n{help_content}\n\n")



import pydoc
import vectorbt

class_names = [vectorbt.utils, vectorbt.data, vectorbt.generic, vectorbt.indicators, vectorbt.signals, vectorbt.records, vectorbt.portfolio, vectorbt.labels]

with open('vectorbt_class_help.txt', 'w', encoding='utf-8') as f:  # 使用UTF-8编码打开文件
    for class_name in class_names:
        help_content = pydoc.render_doc(class_name)
        f.write(f"Help for {class_name.__name__}:\n{help_content}\n\n")


import pydoc
import sys
import vectorbt
# 保存原有的 pager 函数
old_pager = pydoc.pager

# 定义一个新的 pager 函数,直接打印输出
def new_pager(text):
    sys.stdout.write(text)

# 临时替换 pager 函数
pydoc.pager = new_pager
help(vectorbt.utils)

# 还原原有的 pager 函数
pydoc.pager = old_pager




import vectorbt

class_names = [vectorbt.utils, vectorbt.data, vectorbt.generic, vectorbt.indicators, vectorbt.signals, vectorbt.records, vectorbt.portfolio, vectorbt.labels]

with open('vectorbt_class_help.txt', 'w') as f:
    for class_name in class_names:
        help_content = help(class_name)
        f.write(f"Help for {class_name.__name__}:\n{help_content}\n\n")
        
        
        
        
import vectorbt

class_names = [vectorbt.utils, vectorbt.data, vectorbt.generic, vectorbt.indicators, vectorbt.signals, vectorbt.records, vectorbt.portfolio, vectorbt.labels]

with open('vectorbt_class_help.txt', 'w') as f:
    for class_name in class_names:
        help_content = f"Help for {class_name.__name__}:\n{help(class_name)}\n\n"
        f.write(help_content)



import vectorbt

class_names = [vectorbt.utils, vectorbt.data, vectorbt.generic, vectorbt.indicators, vectorbt.signals, vectorbt.records, vectorbt.portfolio, vectorbt.labels]

with open('vectorbt_class_help.txt', 'w') as f:
    for class_name in class_names:
        help_content = f"Help for {class_name.__name__}:\n{help(class_name)}\n\n"   #这句会导致程序在终端分页输出文字需人工翻页不符合要求，要求相应帮助文档的文字内容直接赋值给变量。请改写。
        f.write(help_content)