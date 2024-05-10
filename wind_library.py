import os
 
#list去重复项并按数字小到大，字母a-z重新排序
def unique_sort_list(input_list):
    # 去重复项
    unique_list = list(set(input_list))
    # 按数字小到大排序
    unique_list.sort(key=lambda x: (isinstance(x, int), x) if isinstance(x, (int, float)) else (False, x))
    # 按字母a-z重新排序
    unique_list.sort(key=lambda x: (isinstance(x, str), x.lower()) if isinstance(x, str) else (False, x))
    return unique_list

'''
# task1: 写一个合并多个文件的文本内容到一个文件的python功能函数
函数名：Merge_into_one_file, 参数(path, filetype, newfilename)
新文件的格式："# " + 原文件名称 + "：" 占一行，然后是对应的文本内容，再插入一空行间隔。以此类推
保存到原路径。
要求回复前自行举例试运行验证代码，如果有报错请解除到无报错再回复最终答案。
'''
# 合并多个文件的文本内容到一个文件
def Merge_into_one_file(path, filetype, newfilename):
    with open(os.path.join(path, newfilename), 'w', encoding='utf-8') as outfile:
        for file in os.listdir(path):
            if file.endswith(filetype):
                with open(os.path.join(path, file), 'r', encoding='utf-8') as infile:
                    outfile.write("# " + file + "：\n")
                    outfile.write(infile.read())
                    outfile.write("\n\n")

# 示例用法

# Merge_into_one_file("D:\\document\\python\\QuantitativeTrading\\ccxt\\example_py", "py", "ccxt_example_py.txt")