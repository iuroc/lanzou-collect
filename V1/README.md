# 蓝奏云文件列表采集

## 操作流程

1. 将数据源写入到 [`未校验数据源.txt`](数据源/未校验数据源.txt)
2. 运行 [`采集文件列表.py`](采集文件列表.py)，将自动校验数据源，采集文件列表时，将使用 [`校验成功数据源.txt`](数据源/校验成功数据源.txt) 中的数据源

## 采集结果

- 我们有采集完成的文件，你可以[在此页面下载](https://github.com/oyps/lanzou-collect/releases)

## 打包与使用

1. 运行下面的命令，将程序打包成 EXE（[`dist/采集文件列表.exe`](dist/采集文件列表.exe)）
    ```bash
    pyinstaller -F 采集文件列表.py
    ```
2. 将数据源文件夹放到 EXE 所在目录
3. 双击运行 EXE 程序

## 关于项目

- 作者：欧阳鹏
- 主页：htps://apee.top
- 开发日期：2023 年 2 月 8 日