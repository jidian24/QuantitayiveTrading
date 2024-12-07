import win32com.client

# 创建 Excel 应用程序的实例
excel = win32com.client.Dispatch('Excel.Application')

# 可见性设置
excel.Visible = True

# 添加一个工作簿
workbook = excel.Workbooks.Add()

# 选择活动工作表
sheet = workbook.ActiveSheet

# 在单元格中写入数据
sheet.Cells(1, 1).Value = 'Hello, Excel!'
sheet.Cells(1, 2).Value = 'This is a test.'

# 保存工作簿
workbook.SaveAs('test.xlsx')

# 关闭 Excel
excel.Quit()