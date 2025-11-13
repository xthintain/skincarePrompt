"""
系统管理API
提供数据库初始化、数据导入、模型训练等管理功能
"""
from flask import Blueprint, jsonify, request
import os
import sys
import subprocess
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

admin_bp = Blueprint('admin', __name__)

# 任务状态存储
task_status = {
    'init_database': {'status': 'idle', 'message': ''},
    'import_data': {'status': 'idle', 'message': ''},
    'train_model': {'status': 'idle', 'message': ''},
}


def run_script_async(script_name, task_key):
    """异步运行脚本"""
    global task_status
    task_status[task_key] = {'status': 'running', 'message': '正在执行...'}

    try:
        # 获取backend目录 (从 backend/src/api/v1/admin.py 往上4层到backend/)
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

        # 脚本路径（backend/scripts/xxx.py）
        script_path = os.path.join(current_dir, 'scripts', script_name)

        # 确保脚本文件存在
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"脚本文件不存在: {script_path}")

        # 运行脚本，设置工作目录为backend目录
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            cwd=current_dir,  # 设置工作目录
            timeout=300  # 5分钟超时
        )

        if result.returncode == 0:
            task_status[task_key] = {
                'status': 'success',
                'message': '执行成功',
                'output': result.stdout
            }
        else:
            task_status[task_key] = {
                'status': 'error',
                'message': '执行失败',
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        task_status[task_key] = {
            'status': 'error',
            'message': '执行超时'
        }
    except Exception as e:
        task_status[task_key] = {
            'status': 'error',
            'message': f'执行出错: {str(e)}'
        }


@admin_bp.route('/admin/init-database', methods=['POST'])
def init_database():
    """初始化数据库"""
    try:
        # 在新线程中运行
        thread = threading.Thread(
            target=run_script_async,
            args=('init_database.py', 'init_database')
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': '数据库初始化任务已启动',
            'task_id': 'init_database'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/admin/import-data', methods=['POST'])
def import_data():
    """导入数据"""
    try:
        # 在新线程中运行
        thread = threading.Thread(
            target=run_script_async,
            args=('parse_skincare_data.py', 'import_data')
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': '数据导入任务已启动',
            'task_id': 'import_data'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/admin/train-model', methods=['POST'])
def train_model():
    """训练ML模型"""
    try:
        # 在新线程中运行
        thread = threading.Thread(
            target=run_script_async,
            args=('train_skincare_ml.py', 'train_model')
        )
        thread.start()

        return jsonify({
            'success': True,
            'message': 'ML模型训练任务已启动',
            'task_id': 'train_model'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@admin_bp.route('/admin/task-status/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    if task_id in task_status:
        return jsonify({
            'success': True,
            'task_id': task_id,
            'status': task_status[task_id]
        })
    else:
        return jsonify({
            'success': False,
            'error': '任务不存在'
        }), 404


@admin_bp.route('/admin/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        from src.config import SessionLocal
        from sqlalchemy import text

        # 测试数据库连接
        session = SessionLocal()
        session.execute(text('SELECT 1'))
        session.close()

        # 检查ML模型文件
        model_dir = 'backend/models/skincare_ml'
        model_files = [
            'tfidf_vectorizer.pkl',
            'tfidf_matrix.pkl',
            'knn_model.pkl',
            'products_data.pkl'
        ]

        models_exist = all([
            os.path.exists(os.path.join(model_dir, f))
            for f in model_files
        ])

        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'connected',
            'models': 'loaded' if models_exist else 'not_found',
            'api_version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@admin_bp.route('/admin/system-info', methods=['GET'])
def system_info():
    """获取系统信息"""
    try:
        from src.config import SessionLocal
        from sqlalchemy import text

        session = SessionLocal()

        # 获取商品统计
        total_products = session.execute(text("SELECT COUNT(*) FROM skincare_products")).scalar()
        jd_count = session.execute(text("SELECT COUNT(*) FROM skincare_products WHERE 平台='JD'")).scalar()
        tb_count = session.execute(text("SELECT COUNT(*) FROM skincare_products WHERE 平台='TB'")).scalar()

        session.close()

        # 检查模型文件
        model_dir = 'backend/models/skincare_ml'
        model_info = {}

        if os.path.exists(model_dir):
            for f in os.listdir(model_dir):
                if f.endswith('.pkl'):
                    path = os.path.join(model_dir, f)
                    size = os.path.getsize(path)
                    model_info[f] = f"{size / 1024:.1f} KB"

        return jsonify({
            'success': True,
            'database': {
                'total_products': total_products,
                'jd_products': jd_count,
                'tb_products': tb_count
            },
            'models': model_info,
            'tasks': task_status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
