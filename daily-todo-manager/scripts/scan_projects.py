#!/usr/bin/env python3
"""
扫描 projects/*.md 所有项目文件，提取元数据和未完成任务，写入缓存。

用法:
  python scan_projects.py                    # 使用默认 $TODO_DIR
  python scan_projects.py --todo-dir /path   # 指定 TODO 目录

缓存位置: $TODO_DIR/memory/project-tasks-cache.json
"""
import json, os, re, sys, argparse
from datetime import date


def get_default_todo_dir():
    todo_dir = os.environ.get("TODO_DIR", "")
    if not todo_dir:
        print("错误: 请设置 TODO_DIR 环境变量，或用 --todo-dir 指定路径", file=sys.stderr)
        sys.exit(1)
    return todo_dir


def parse_meta(lines: list[str]) -> dict:
    """从文件头部提取 **key**：value 元数据"""
    meta = {"deadline": None, "priority": "中", "status": "活跃", "progress": "0%"}
    for line in lines:
        m = re.match(r"\*\*(.+?)\*\*[：:]\s*(.+)", line)
        if not m:
            continue
        k, v = m.group(1).strip(), m.group(2).strip()
        if "截止" in k:
            meta["deadline"] = None if v in ("待定", "无", "") else v
        elif "优先" in k:
            meta["priority"] = v
        elif "状态" in k:
            meta["status"] = v
    return meta


def parse_progress(lines: list[str]) -> str:
    """提取进度百分比"""
    for line in lines:
        m = re.search(r"进度[：:]\s*(\d+%?)", line)
        if m:
            return m.group(1)
    return "0%"


def parse_parent_map(lines: list[str]) -> dict:
    """从文件头部提取父子项目映射"""
    for line in lines:
        m = re.match(r"\*\*子项目\*\*[：:]\s*(.+)", line)
        if m:
            return {child.strip(): True for child in m.group(1).split(",")}
    return {}


def extract_tasks(lines: list[str]) -> list[str]:
    """从任务列表区块提取未完成任务"""
    tasks = []
    in_section = False
    for line in lines:
        if re.match(r"^##\s+(任务列表|🟡\s+活跃临时任务)", line):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            in_section = False
            continue
        if in_section:
            m = re.match(r"^-\s*\[ \]\s*(.+)", line)
            if m:
                task = m.group(1).strip()
                if task and len(task) > 2:
                    tasks.append(task)
    return tasks


def extract_temp_tasks(lines: list[str]) -> list[str]:
    """从临时任务文件的活跃临时任务区块中提取"""
    tasks = []
    in_active = False
    for line in lines:
        if re.match(r"^##\s+🟡\s+活跃临时任务", line):
            in_active = True
            continue
        if in_active and re.match(r"^##\s+", line):
            in_active = False
            continue
        if in_active:
            m = re.match(r"^-\s*\[ \]\s*(.+)", line)
            if m:
                task = m.group(1).strip()
                if task and len(task) > 2:
                    tasks.append(task)
    return tasks


def scan(todo_dir: str):
    projects_dir = os.path.join(todo_dir, "projects")
    cache_dir = os.path.join(todo_dir, "memory")
    cache_path = os.path.join(cache_dir, "project-tasks-cache.json")

    if not os.path.isdir(projects_dir):
        print(f"错误: projects 目录不存在: {projects_dir}", file=sys.stderr)
        sys.exit(1)

    results = {}
    parent_map = {}

    for fname in sorted(os.listdir(projects_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(projects_dir, fname)
        with open(fpath, encoding="utf-8") as f:
            lines = f.readlines()

        # 项目名：取 # 项目：XXX 或从文件名推导
        name = None
        for line in lines[:5]:
            m = re.match(r"^#\s+项目[：:]\s*(.+)", line)
            if m:
                name = m.group(1).strip()
                break
        if not name:
            name = fname.replace(".md", "")

        meta = parse_meta(lines)
        progress = parse_progress(lines)

        # 检查子项目声明
        children = parse_parent_map(lines)
        if children:
            parent_map[name] = list(children.keys())

        if fname == "临时任务.md":
            tasks = extract_temp_tasks(lines)
        else:
            tasks = extract_tasks(lines)

        results[name] = {
            "file": fname,
            "priority": meta["priority"],
            "status": meta["status"],
            "deadline": meta["deadline"],
            "progress": progress,
            "incompleteTasks": tasks,
        }

    # 标记父子关系
    for parent, children in parent_map.items():
        if parent in results:
            results[parent]["isParent"] = True
            results[parent]["childProjects"] = children

    # 读取 config.md 获取 fixedTasks
    fixed_tasks = []
    config_path = os.path.join(todo_dir, "config.md")
    if os.path.exists(config_path):
        with open(config_path, encoding="utf-8") as f:
            in_fixed = False
            for line in f:
                if line.startswith("## 固定任务") or line.startswith("## 每日习惯"):
                    in_fixed = True
                    continue
                if in_fixed and line.startswith("##"):
                    in_fixed = False
                    continue
                if in_fixed:
                    m = re.match(r"^-\s*(.+)", line)
                    if m:
                        fixed_tasks.append(m.group(1).strip())

    cache = {
        "version": "1.0",
        "lastUpdated": date.today().isoformat(),
        "projects": results,
        "fixedTasks": fixed_tasks,
    }

    os.makedirs(cache_dir, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        f.write("\n")

    total_tasks = sum(len(p["incompleteTasks"]) for p in results.values())
    print(f"扫描 {len(results)} 个项目，发现 {total_tasks} 个未完成任务")
    print(f"缓存已写入 {cache_path}")


def main():
    parser = argparse.ArgumentParser(description="扫描项目文件并重建缓存")
    parser.add_argument("--todo-dir", help="TODO 数据目录 (默认 $TODO_DIR)")
    args = parser.parse_args()

    todo_dir = args.todo_dir or get_default_todo_dir()
    scan(todo_dir)


if __name__ == "__main__":
    main()
