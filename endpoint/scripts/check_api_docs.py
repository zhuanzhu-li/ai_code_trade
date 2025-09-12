#!/usr/bin/env python3
"""
API文档同步检查脚本
检查代码中的API端点是否与文档同步
"""

import os
import sys
import re
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def extract_api_routes(file_path):
    """从Python文件中提取API路由"""
    routes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 匹配 @api_bp.route 装饰器
        pattern = r'@api_bp\.route\([\'"]([^\'"]+)[\'"],\s*methods=\[([^\]]+)\]\)'
        matches = re.findall(pattern, content)
        
        for path, methods in matches:
            # 解析HTTP方法
            methods_list = [m.strip().strip("'\"") for m in methods.split(',')]
            for method in methods_list:
                routes.append({
                    'path': path,
                    'method': method.upper(),
                    'file': file_path
                })
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return routes

def extract_documented_routes(doc_path):
    """从API文档中提取已记录的路由"""
    routes = []
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 匹配文档中的API路径
        pattern = r'\*\*(GET|POST|PUT|DELETE)\*\*\s*`([^`]+)`'
        matches = re.findall(pattern, content)
        
        for method, path in matches:
            routes.append({
                'path': path,
                'method': method.upper(),
                'file': doc_path
            })
            
    except Exception as e:
        print(f"Error reading {doc_path}: {e}")
        
    return routes

def check_api_sync():
    """检查API同步状态"""
    print("🔍 检查API文档同步状态...")
    
    # 获取所有Python文件中的API路由
    routes_dir = project_root / 'app'
    all_routes = []
    
    for py_file in routes_dir.glob('*.py'):
        if py_file.name != '__init__.py':
            routes = extract_api_routes(py_file)
            all_routes.extend(routes)
    
    # 获取文档中的路由
    doc_path = project_root / 'API_DOCUMENTATION.md'
    documented_routes = extract_documented_routes(doc_path)
    
    print(f"📊 统计结果:")
    print(f"   代码中的API端点: {len(all_routes)}")
    print(f"   文档中的API端点: {len(documented_routes)}")
    
    # 检查缺失的文档
    code_routes = {(r['path'], r['method']) for r in all_routes}
    doc_routes = {(r['path'], r['method']) for r in documented_routes}
    
    missing_in_docs = code_routes - doc_routes
    extra_in_docs = doc_routes - code_routes
    
    if missing_in_docs:
        print(f"\n❌ 文档中缺失的API端点 ({len(missing_in_docs)}个):")
        for path, method in sorted(missing_in_docs):
            print(f"   {method} {path}")
    
    if extra_in_docs:
        print(f"\n⚠️  文档中多余的API端点 ({len(extra_in_docs)}个):")
        for path, method in sorted(extra_in_docs):
            print(f"   {method} {path}")
    
    if not missing_in_docs and not extra_in_docs:
        print("\n✅ API文档与代码完全同步！")
        return True
    else:
        print(f"\n📈 文档覆盖率: {len(doc_routes & code_routes) / len(code_routes) * 100:.1f}%")
        return False

def generate_api_report():
    """生成API报告"""
    print("\n📋 生成API报告...")
    
    # 获取所有API路由
    routes_dir = project_root / 'app'
    all_routes = []
    
    for py_file in routes_dir.glob('*.py'):
        if py_file.name != '__init__.py':
            routes = extract_api_routes(py_file)
            all_routes.extend(routes)
    
    # 按模块分组
    modules = {}
    for route in all_routes:
        module = route['file'].stem
        if module not in modules:
            modules[module] = []
        modules[module].append(route)
    
    # 生成报告
    report = {
        'total_endpoints': len(all_routes),
        'modules': {}
    }
    
    for module, routes in modules.items():
        report['modules'][module] = {
            'count': len(routes),
            'endpoints': routes
        }
    
    # 保存报告
    report_path = project_root / 'api_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📄 API报告已保存到: {report_path}")
    
    return report

def main():
    """主函数"""
    print("🚀 API文档同步检查工具")
    print("=" * 50)
    
    # 检查同步状态
    is_synced = check_api_sync()
    
    # 生成报告
    report = generate_api_report()
    
    # 输出建议
    print("\n💡 建议:")
    if not is_synced:
        print("   1. 使用Flask-RESTX自动生成API文档")
        print("   2. 定期运行此脚本检查同步状态")
        print("   3. 在CI/CD中集成文档检查")
    else:
        print("   1. 继续保持文档与代码同步")
        print("   2. 考虑使用自动化工具减少手动维护")
    
    return 0 if is_synced else 1

if __name__ == '__main__':
    sys.exit(main())
