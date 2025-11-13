#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
部署检查脚本
检查项目部署环境是否正确配置
"""
import os
import sys

def check_python_version():
    """检查Python版本"""
    print("=" * 60)
    print("1. 检查Python版本")
    print("=" * 60)
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 10:
        print("✅ Python版本符合要求 (>= 3.10)")
        return True
    else:
        print("❌ Python版本不符合要求，需要 >= 3.10")
        return False

def check_directories():
    """检查必要的目录结构"""
    print("\n" + "=" * 60)
    print("2. 检查目录结构")
    print("=" * 60)

    required_dirs = [
        '../data',
        '../data/JD',
        '../data/TB',
        'models',
        'models/skincare_ml',
        'scripts'
    ]

    all_exist = True
    for dir_path in required_dirs:
        exists = os.path.exists(dir_path)
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}: {'存在' if exists else '不存在'}")
        if not exists:
            all_exist = False

    return all_exist

def check_data_files():
    """检查数据文件"""
    print("\n" + "=" * 60)
    print("3. 检查数据文件")
    print("=" * 60)

    jd_dir = '../data/JD'
    tb_dir = '../data/TB'

    all_exist = True

    if os.path.exists(jd_dir):
        jd_files = [f for f in os.listdir(jd_dir) if f.endswith('.html')]
        print(f"✅ 京东HTML文件: {len(jd_files)} 个")
    else:
        print(f"❌ 京东数据目录不存在: {jd_dir}")
        all_exist = False

    if os.path.exists(tb_dir):
        tb_files = [f for f in os.listdir(tb_dir) if f.endswith('.html')]
        print(f"✅ 淘宝HTML文件: {len(tb_files)} 个")
    else:
        print(f"❌ 淘宝数据目录不存在: {tb_dir}")
        all_exist = False

    return all_exist

def check_model_files():
    """检查ML模型文件"""
    print("\n" + "=" * 60)
    print("4. 检查ML模型文件")
    print("=" * 60)

    model_dir = 'models/skincare_ml'
    required_models = [
        'tfidf_vectorizer.pkl',
        'tfidf_matrix.pkl',
        'knn_model.pkl',
        'products_data.pkl'
    ]

    all_exist = True
    if os.path.exists(model_dir):
        for model_file in required_models:
            model_path = os.path.join(model_dir, model_file)
            exists = os.path.exists(model_path)
            status = "✅" if exists else "❌"
            if exists:
                size = os.path.getsize(model_path) / 1024  # KB
                print(f"{status} {model_file}: {size:.1f} KB")
            else:
                print(f"{status} {model_file}: 不存在")
                all_exist = False
    else:
        print(f"❌ 模型目录不存在: {model_dir}")
        all_exist = False

    return all_exist

def check_dependencies():
    """检查Python依赖包"""
    print("\n" + "=" * 60)
    print("5. 检查Python依赖")
    print("=" * 60)

    required_packages = {
        'flask': 'Flask',
        'sqlalchemy': 'SQLAlchemy',
        'psycopg2': 'psycopg2-binary',
        'sklearn': 'scikit-learn',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'jieba': 'jieba'
    }

    all_installed = True
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {pip_name}: 已安装")
        except ImportError:
            print(f"❌ {pip_name}: 未安装")
            all_installed = False

    return all_installed

def check_database():
    """检查数据库连接"""
    print("\n" + "=" * 60)
    print("6. 检查数据库连接")
    print("=" * 60)

    try:
        # 尝试导入配置
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.config import SessionLocal
        from sqlalchemy import text

        session = SessionLocal()
        result = session.execute(text('SELECT 1')).scalar()
        session.close()

        if result == 1:
            print("✅ 数据库连接成功")
            return True
        else:
            print("❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def check_environment_variables():
    """检查环境变量"""
    print("\n" + "=" * 60)
    print("7. 检查环境变量")
    print("=" * 60)

    pythonpath = os.environ.get('PYTHONPATH', '')
    print(f"PYTHONPATH: {pythonpath if pythonpath else '(未设置)'}")

    if pythonpath:
        print("✅ PYTHONPATH已设置")
        return True
    else:
        print("⚠️  PYTHONPATH未设置 (运行时需要设置)")
        return True  # 不是必须的

def main():
    """主函数"""
    print("\n" + "🔍 " * 15)
    print("护肤品推荐系统 - 部署环境检查")
    print("🔍 " * 15 + "\n")

    # 切换到scripts所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"当前工作目录: {os.getcwd()}\n")

    results = []

    # 执行所有检查
    results.append(("Python版本", check_python_version()))
    results.append(("目录结构", check_directories()))
    results.append(("数据文件", check_data_files()))
    results.append(("模型文件", check_model_files()))
    results.append(("Python依赖", check_dependencies()))
    results.append(("数据库连接", check_database()))
    results.append(("环境变量", check_environment_variables()))

    # 总结
    print("\n" + "=" * 60)
    print("检查结果总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")

    print(f"\n通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有检查通过！环境配置正确。")
        return 0
    else:
        print("\n⚠️  部分检查失败，请根据上述提示修复问题。")
        print("\n常见问题解决方案:")
        print("1. 数据目录不存在: 确保data/JD和data/TB目录存在且包含HTML文件")
        print("2. 模型文件不存在: 运行 'python scripts/train_skincare_ml.py' 训练模型")
        print("3. Python依赖未安装: 运行 'pip install -r requirements.txt'")
        print("4. 数据库连接失败: 检查PostgreSQL是否运行，配置是否正确")
        print("5. PYTHONPATH未设置: 启动时使用 'PYTHONPATH=xxx python src/app.py'")
        return 1

if __name__ == '__main__':
    sys.exit(main())
