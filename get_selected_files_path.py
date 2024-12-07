import subprocess
# import pyperclip

def get_selected_files_path():
    """获取选中的文件路径"""
    try:
        # 通过 PowerShell 获取选中的文件路径
        command = ['powershell', '-command', 'Get-Clipboard -Format FileDropList']
        output = subprocess.check_output(command, text=True)
        # 按行分割输出，过滤掉空行
        files = [line for line in output.splitlines() if line]
        return files
    except Exception as e:
        print(f"获取选中文件失败: {e}")
        return []

def main():
    # 获取选中的文件路径
    selected_files = get_selected_files_path()

    if not selected_files:
        print("没有选中的文件")
        return

    # 将文件名组合为字符串
    file_names = "\n".join(selected_files)

    # 将文件名写入剪贴板
    # try:
    #     pyperclip.copy(file_names)
    #     print("选中的文件名已写入剪贴板")
    # except Exception as e:
    #     print(f"写入剪贴板失败: {e}")

if __name__ == "__main__":
    main()
