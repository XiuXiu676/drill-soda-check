@echo off
echo ========================================
echo  正在设置 Python 虚拟环境...
echo ========================================

echo 1. 删除旧的虚拟环境（如果存在）...
if exist .venv (
    rmdir /s /q .venv
    echo 旧环境已删除。
)

echo 2. 创建新的虚拟环境...
python -m venv .venv

echo 3. 激活虚拟环境...
call .venv\Scripts\activate

echo 4. 升级 pip...
python -m pip install --upgrade pip

echo 5. 安装项目依赖...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo 警告: requirements.txt 不存在!
)

echo 6. 安装完成！
echo ========================================
echo  使用方法:
echo  1. 激活环境: .venv\Scripts\activate
echo  2. 运行项目: python main.py
echo ========================================
pause