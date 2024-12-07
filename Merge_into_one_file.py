import os
import nbformat

def Merge_into_one_file(path, filetype, newfilename, Subfolder=False):
    with open(os.path.join(path, newfilename), 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(filetype):
                    file_path = os.path.join(root, file)
                    if filetype == 'ipynb':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            notebook = nbformat.read(f, as_version=4)
                        for cell in notebook.cells:
                            if cell.cell_type == 'code':
                                outfile.write("# " + os.path.relpath(file_path, path) + ":\n")
                                outfile.write(cell.source)
                                outfile.write("\n\n")
                    else:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write("# " + os.path.relpath(file_path, path) + ":\n")
                            outfile.write(infile.read())
                            outfile.write("\n\n")
            if not Subfolder:
                break

# 示例用法
# Merge_into_one_file("D:\\document\\python\\QuantitativeTrading\\ccxt\\example_py", "ipynb", "ccxt_example_ipynb.txt", Subfolder=True)
Merge_into_one_file("D:\\document\\python\\QuantitativeTrading\\vectorbt-master", "py", "vectorbr_Source code.txt", Subfolder=True)