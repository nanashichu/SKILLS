#!/usr/bin/env python3
"""
初始化 TODO 目录结构。
首次使用时运行，创建所有必需的目录和默认配置文件。

用法:
  python init_todo_dir.py                    # 使用默认 $TODO_DIR
  python init_todo_dir.py --todo-dir /path   # 指定 TODO 目录
"""
import os, sys, argparse


def create_if_not_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"  创建目录: {path}")


def create_file_if_not_exists(path, content):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  创建文件: {path}")


def main():
    parser = argparse.ArgumentParser(description="初始化 TODO 目录结构")
    parser.add_argument("--todo-dir", help="TODO 数据目录 (默认 $TODO_DIR)")
    args = parser.parse_args()

    todo_dir = args.todo_dir or os.environ.get("TODO_DIR", "")
    if not todo_dir:
        print("错误: 请设置 TODO_DIR 环境变量，或用 --todo-dir 指定路径")
        print("示例: export TODO_DIR=~/my-todos")
        sys.exit(1)

    todo_dir = os.path.expanduser(todo_dir)
    print(f"初始化 TODO 目录: {todo_dir}\n")

    # 目录结构
    dirs = [
        todo_dir,
        os.path.join(todo_dir, "daily"),
        os.path.join(todo_dir, "weekly"),
        os.path.join(todo_dir, "projects"),
        os.path.join(todo_dir, "reviews"),
        os.path.join(todo_dir, "memory"),
    ]
    for d in dirs:
        create_if_not_exists(d)

    # 默认配置文件
    config_content = """# TODO 系统配置

## 固定任务（每日提醒，用 - 列出）
- 读论文30分钟
- 整理当日笔记

## 任务类型关键词
- 实证研究：回归、面板、Stata、数据、基准回归、DiD
- 编程开发：代码、开发、调试、部署、skill
- 论文写作：写作、撰写、修改、综述
- 会议沟通：会议、交流、讨论、汇报

## 风险阈值
- 紧急截止天数：3
- 项目停滞警告天数：5
- 低效连续天数：3
"""
    create_file_if_not_exists(os.path.join(todo_dir, "config.md"), config_content)

    # 默认 Guard 配置
    guard_content = """{
  "guards": [
    {
      "id": "no_overdue",
      "name": "无逾期任务",
      "level": "critical",
      "enabled": true,
      "check": "所有项目 deadline > today 或 已完成",
      "action": "列出所有逾期任务，要求用户确认或重新安排"
    },
    {
      "id": "efficiency_floor",
      "name": "效率下限",
      "level": "warning",
      "enabled": true,
      "check": "连续3天完成率 ≥ 日均50%",
      "action": "提示效率下降，建议调整任务量或检查时间分配"
    },
    {
      "id": "habit_continuity",
      "name": "习惯连续性",
      "level": "warning",
      "enabled": true,
      "check": "fixedTasks 中的任务间隔 ≤ 2天",
      "action": "提醒恢复习惯任务"
    }
  ]
}
"""
    create_file_if_not_exists(os.path.join(todo_dir, "memory", "guard-config.json"), guard_content.strip())

    # 空的临时任务文件
    temp_task_content = """# 项目：临时任务

**创建日期**：{today}
**状态**：活跃

## 🟡 活跃临时任务

（暂无）

## ✅ 历史记录

（暂无）
""".format(today=__import__('datetime').date.today().isoformat())
    create_file_if_not_exists(os.path.join(todo_dir, "projects", "临时任务.md"), temp_task_content)

    print(f"\n初始化完成!")
    print(f"数据目录: {todo_dir}")
    print(f"下一步: 在 Claude Code settings.json 中设置环境变量:")
    print(f'  "env": {{"TODO_DIR": "{todo_dir}"}}')


if __name__ == "__main__":
    main()
