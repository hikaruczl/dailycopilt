#!/usr/bin/env python3
"""
Daily Copilot Backend 启动脚本
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        sys.exit(1)
    print(f"✓ Python版本: {sys.version}")

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        print("✓ 核心依赖已安装")
        return True
    except ImportError:
        print("⚠ 缺少依赖，正在安装...")
        return False

def install_dependencies():
    """安装依赖"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        sys.exit(1)

def setup_environment():
    """设置环境"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("⚠ 未找到.env文件，正在创建...")
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("✓ 已创建.env文件，请编辑配置")
    
    # 创建上传目录
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    print("✓ 上传目录已准备")

def start_server():
    """启动服务器"""
    print("\n🚀 启动Daily Copilot后端服务...")
    print("=" * 50)
    
    try:
        from app.main import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("Daily Copilot Backend 启动器")
    print("=" * 30)
    
    # 检查Python版本
    check_python_version()
    
    # 检查并安装依赖
    if not check_dependencies():
        install_dependencies()
    
    # 设置环境
    setup_environment()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()
