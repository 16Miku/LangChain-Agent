#!/usr/bin/env python3
"""
OpenAPI 文档导出脚本

为所有微服务生成 OpenAPI JSON 和 YAML 文件。

使用方法:
    python scripts/export_openapi.py

输出目录:
    docs/openapi/
"""

import json
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def export_openapi(service_name: str, app_module: str, output_dir: Path):
    """
    导出单个服务的 OpenAPI 文档

    Args:
        service_name: 服务名称
        app_module: FastAPI 应用模块路径
        output_dir: 输出目录
    """
    try:
        # 动态导入服务模块
        import importlib
        module = importlib.import_module(app_module)
        app = getattr(module, 'app')

        # 获取 OpenAPI schema
        openapi_schema = app.openapi()

        # 保存为 JSON
        json_path = output_dir / f"{service_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        print(f"✓ {service_name}: {json_path}")

        # 保存为 YAML
        try:
            import yaml
            yaml_path = output_dir / f"{service_name}.yaml"
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(openapi_schema, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"✓ {service_name}: {yaml_path}")
        except ImportError:
            print(f"⚠ {service_name}: YAML 导出跳过 (需要安装 pyyaml)")

        return True

    except Exception as e:
        print(f"✗ {service_name}: 导出失败 - {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("OpenAPI 文档导出")
    print("=" * 60)

    # 创建输出目录
    output_dir = project_root / "docs" / "openapi"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n输出目录: {output_dir}\n")

    # 服务配置
    services = [
        ("auth-service", "backend.auth-service.app.main"),
        ("chat-service", "backend.chat-service.app.main"),
        ("rag-service", "backend.rag-service.app.main"),
        ("presentation-service", "backend.presentation-service.app.main"),
    ]

    # 由于模块路径包含连字符，需要特殊处理
    # 这里我们直接读取各服务的 main.py 并提取 OpenAPI

    results = []

    for service_name, _ in services:
        service_dir = project_root / "backend" / service_name
        if not service_dir.exists():
            print(f"✗ {service_name}: 目录不存在")
            results.append(False)
            continue

        # 添加服务目录到路径
        sys.path.insert(0, str(service_dir))

        try:
            # 导入服务的 app
            from app.main import app

            # 获取 OpenAPI schema
            openapi_schema = app.openapi()

            # 保存为 JSON
            json_path = output_dir / f"{service_name}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
            print(f"✓ {service_name}: {json_path}")

            # 保存为 YAML
            try:
                import yaml
                yaml_path = output_dir / f"{service_name}.yaml"
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(openapi_schema, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
                print(f"✓ {service_name}: {yaml_path}")
            except ImportError:
                print(f"⚠ {service_name}: YAML 导出跳过 (需要安装 pyyaml)")

            results.append(True)

        except Exception as e:
            print(f"✗ {service_name}: 导出失败 - {e}")
            results.append(False)
        finally:
            # 清理导入的模块
            modules_to_remove = [m for m in sys.modules if m.startswith('app.')]
            for m in modules_to_remove:
                del sys.modules[m]
            sys.path.remove(str(service_dir))

    # 打印汇总
    print("\n" + "=" * 60)
    success_count = sum(results)
    total_count = len(results)
    print(f"导出完成: {success_count}/{total_count} 个服务成功")

    if success_count < total_count:
        print("\n提示: 部分服务导出失败，可能是因为:")
        print("  1. 服务依赖未安装")
        print("  2. 环境变量未配置")
        print("  3. 数据库连接问题")
        print("\n建议单独启动各服务后访问 /docs 查看 OpenAPI 文档")

    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
