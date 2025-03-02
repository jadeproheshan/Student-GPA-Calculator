# 从教务网站下载自己的成绩，另存为"scores.xlsx"
import pandas as pd
#path = "E:\%E5%85%A8%E9%83%A8%E6%88%90%E7%BB%A9%E6%9F%A5%E8%AF%A2 2.xlsx"
path="D:\soft\新建文件夹\全部成绩查询.xlsx"
df= pd.read_excel(path)

df = df[(df['课程类别'] != '通识教育课程') & (df['是否主修'] == '是') & (df['等级成绩'].isnull()) & (df['课程性质'] != '任选')]

df.loc[:,'绩点学分'] = df['绩点'] * df['学分']

semester = df.groupby('学年学期').agg({'绩点学分': 'sum', '学分': 'sum'}).reset_index()

semester.loc[:,'平均绩点'] = semester['绩点学分'] / semester['学分']

total_gpa = semester['绩点学分'].sum() / semester['学分'].sum()
total_ysx = semester['学分'].sum()

print("每个学期的平均绩点：")
print(semester[['学年学期', '平均绩点']])

print("\n总平均绩点：")
print(total_gpa)

print("\n总学分：")
print(total_ysx)