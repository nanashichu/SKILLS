#!/usr/bin/env python3
"""初始化 daily-todo-manager 数据目录。

在指定的 TODO_DIR 下创建 daily/、projects/、memory/、weekly/、reviews/ 目录，
以及默认配置文件、缓存文件、临时任务文件。

用法：
    python init_todo_dir.py                          # 使用 $TODO_DIR 环境变量
    python init_todo_dir.py --todo-dir ~/mytodos     # 指定目录
    python init_todo_dir.py --todo-dir ~/mytodos --force  # 强制覆盖已有文件
"""

import argparse
import json
import os
import sys
from datetime import datetime


def create_directory(path: str) -> None:
    """创建目录，已存在则跳过。"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  ✓ 创建目录：{path}")
    else:
        print(f"  - 已存在：{path}")


def write_file(path: str, content: str, force: bool = False) -> bool:
    """写入文件。已存在且非 force 时跳过，返回是否写入。"""
    if os.path.exists(path) and not force:
        print(f"  - 跳过（已存在）：{path}")
        return False
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ 写入：{path}")
    return True


def init_todo_dir(todo_dir: str, force: bool = False) -> None:
    """初始化数据目录。"""
    print(f"\n📁 初始化 daily-todo-manager 数据目录")
    print(f"   目标：{os.path.abspath(todo_dir)}\n")

    # 1. 目录结构
    print("[1/3] 创建目录结构")
    for sub in ["daily", "projects", "memory", "weekly", "reviews"]:
        create_directory(os.path.join(todo_dir, sub))

    # 2. 配置文件
    print("\n[2/3] 创建配置文件")
    config_md = """# 系统配置

## 固定任务（每日自动提醒）
- （暂无，按需添加，格式：`- 任务描述`）

## 任务类型关键词（用于时间预测）
| 类型 | 关键词 |
|------|--------|
| 实证研究 | 回归、面板、Stata、数据、基准回归、稳健性、内生性、机制 |
| 论文写作 | 论文、写作、修改、草稿、图表、摘要、引言 |
| 文献阅读 | 文献、论文、阅读、PDF、笔记 |
| 数据处理 | 数据、清洗、合并、爬虫、下载 |
| 项目管理 | 项目、规划、汇报、周报 |

## 风险阈值
| 参数 | 默认值 | 说明 |
|------|--------|------|
| urgent_days | 3 | 紧急任务天数阈值 |
| stall_days | 14 | 停滞项目天数阈值 |
| low_efficiency_days | 3 | 连续低效天数阈值 |
"""
    write_file(os.path.join(todo_dir, "config.md"), config_md, force)

    # 3. 数据文件
    print("\n[3/3] 创建数据文件")
    today = datetime.now().strftime("%Y-%m-%d")

    # 项目缓存
    cache = {
        "version": "1.0",
        "lastUpdated": today,
        "projects": {},
        "fixedTasks": [],
    }
    write_file(os.path.join(todo_dir, "memory", "project-tasks-cache.json"),
               json.dumps(cache, ensure_ascii=False, indent=2) + "\n", force)

    # Guard 配置
    guards = {
        "version": "1.0",
        "guards": [
            {
                "name": "no_overdue",
                "description": "不允许因调整导致任务逾期",
                "check": "所有任务截止日期 >= 今天",
                "severity": "critical",
                "enabled": True,
            },
            {
                "name": "efficiency_floor",
                "description": "效率得分不低于历史平均的80%",
                "check": "efficiency_score >= weekly_average * 0.8",
                "severity": "warning",
                "enabled": True,
            },
            {
                "name": "habit_continuity",
                "description": "核心习惯不被跳过",
                "check": "今日包含至少一个习惯任务",
                "severity": "warning",
                "enabled": True,
            },
            {
                "name": "urgent_priority",
                "description": "紧急任务被优先处理",
                "check": "紧急任务排在待办前3位",
                "severity": "warning",
                "enabled": True,
            },
        ],
    }
    write_file(os.path.join(todo_dir, "memory", "guard-config.json"),
               json.dumps(guards, ensure_ascii=False, indent=2) + "\n", force)

    # 任务用时历史
    task_history = {"version": "1.0", "lastUpdated": today, "history": []}
    write_file(os.path.join(todo_dir, "memory", "task-time-history.json"),
               json.dumps(task_history, ensure_ascii=False, indent=2) + "\n", force)

    # 会话上下文
    session_context = {
        "version": "1.0",
        "currentTask": None,
        "lastUpdated": today,
    }
    write_file(os.path.join(todo_dir, "memory", "session-context.json"),
               json.dumps(session_context, ensure_ascii=False, indent=2) + "\n", force)

    # 临时任务
    temp_task = f"""# 项目：临时任务

**创建日期**：{today}
**状态**：活跃

## 🟡 活跃临时任务
- （暂无）

## ✅ 历史记录
（暂无）
"""
    write_file(os.path.join(todo_dir, "projects", "临时任务.md"), temp_task, force)

    print(f"\n✅ 初始化完成！")
    print(f"   下一步：在 Claude Code 中说「早上好」开始使用。")


def main():
    parser = argparse.ArgumentParser(
        description="初始化 daily-todo-manager 数据目录"
    )
    parser.add_argument(
        "--todo-dir",
        default=os.environ.get("TODO_DIR", ""),
        help="数据目录路径（默认使用 $TODO_DIR 环境变量）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制覆盖已有文件",
    )
    args = parser.parse_args()

    if not args.todo_dir:
        print("❌ 错误：未指定目录。")
        print("   方式1：设置环境变量 TODO_DIR")
        print("   方式2：python init_todo_dir.py --todo-dir /你的路径/")
        sys.exit(1)

    todo_dir = os.path.expanduser(args.todo_dir)
    init_todo_dir(todo_dir, args.force)


if __name__ == "__main__":
    main()
