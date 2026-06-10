#!/usr/bin/env python3
"""
扫描所有项目文件，生成 project-tasks-cache.json

用法: python scan_projects.py [--output <path>]

默认输出到 G:/【20260401】每日待办/memory/project-tasks-cache.json
"""

import json, os, re, sys
from datetime import datetime
from pathlib import Path

PROJECTS_DIR = Path(r"G:\【20260401】每日待办\projects")
DEFAULT_OUTPUT = Path(r"G:\【20260401】每日待办\memory\project-tasks-cache.json")

# 父项目 → 子项目列表（按文件名关键词）
PARENT_CHILD_MAP = {
    "博士大论文": ["第一篇实证", "第二篇实证"],
}


def parse_project_file(filepath: Path) -> dict | None:
    """解析单个项目文件，返回项目数据或 None"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [WARN] 无法读取 {filepath.name}: {e}", file=sys.stderr)
        return None

    lines = content.split("\n")

    # 项目名：第一行 # 项目：XXX
    name = None
    for line in lines[:3]:
        m = re.match(r"^#\s*项目[：:]\s*(.+)$", line)
        if m:
            name = m.group(1).strip()
            break
    if not name:
        # 从文件名推导
        stem = filepath.stem
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)

    # 元数据：**字段**：值 — 必须锚定到行首的 ** 前缀，避免匹配正文中的子串
    priority = "中"
    status = "活跃"
    deadline = None
    for line in lines[:20]:
        stripped = line.strip()
        # 优先级
        if re.match(r"\*\*优先级\*\*[：:]", stripped):
            m = re.search(r"[高中低]", stripped)
            if m:
                priority = m.group()
        # 状态
        elif re.match(r"\*\*状态\*\*[：:]", stripped):
            m = re.search(r"\*\*状态\*\*[：:]\s*(.+)$", stripped)
            if m:
                val = m.group(1).strip().rstrip("*")
                if len(val) < 20:  # 防污染：状态值应该很短
                    status = val
        # 截止日期
        elif re.match(r"\*\*截止日期\*\*[：:]", stripped):
            m = re.search(r"\*\*截止日期\*\*[：:]\s*(.+)$", stripped)
            if m:
                d = m.group(1).strip()
                if d not in ("待定", "无", ""):
                    deadline = d

    # 解析任务列表
    incomplete_tasks = []
    progress_str = "0%"
    in_task_section = False
    in_progress_section = False

    for line in lines:
        if line.startswith("## 📊 项目进度") or line.startswith("## 项目进度"):
            in_progress_section = True
            in_task_section = False
            continue
        if line.startswith("## 任务列表") or line.startswith("## 📋 任务列表"):
            in_task_section = True
            in_progress_section = False
            continue
        if line.startswith("##") and not line.startswith("###"):
            in_task_section = False
            in_progress_section = False

        if in_progress_section:
            m = re.search(r"进度[：:]\s*(\d+)%", line)
            if m:
                progress_str = f"{m.group(1)}%"

        if in_task_section:
            # 匹配 - [ ] 或 - [✅] 或 - [x]
            m = re.match(r"-\s*\[([\s✅xX])\]\s*(.+)", line)
            if m:
                checkbox = m.group(1).strip()
                task_text = m.group(2).strip()
                # 清理日期后缀
                task_text = re.sub(r"\s*✅\s*\d{4}-\d{2}-\d{2}.*$", "", task_text)
                if not checkbox:  # [ ] → 未完成
                    incomplete_tasks.append(task_text)

    # 判断是否为父项目
    is_parent = False
    child_projects = []
    for parent_key, children in PARENT_CHILD_MAP.items():
        if parent_key in name:
            is_parent = True
            child_projects = children[:]

    # 去重 (有些任务文本含冗余)
    seen = set()
    unique_tasks = []
    for t in incomplete_tasks:
        key = t.strip()[:60]
        if key not in seen:
            seen.add(key)
            unique_tasks.append(t)

    return {
        "file": filepath.name,
        "priority": priority,
        "status": status,
        "deadline": deadline,
        "progress": progress_str,
        "incompleteTasks": unique_tasks,
        "isParent": is_parent,
        "childProjects": child_projects if is_parent else None,
    }


def scan_all() -> dict:
    """扫描所有项目文件，返回完整缓存数据"""
    if not PROJECTS_DIR.exists():
        print(f"项目目录不存在: {PROJECTS_DIR}", file=sys.stderr)
        return {"version": "1.0", "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
                "projects": {}, "fixedTasks": []}

    projects = {}
    for f in sorted(PROJECTS_DIR.glob("*.md")):
        result = parse_project_file(f)
        if result is None:
            continue
        name = f.stem
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
        projects[name] = result

    # 移除 isParent/childProjects 为 None 的字段，整洁输出
    for pdata in projects.values():
        if not pdata.get("isParent"):
            del pdata["isParent"]
            del pdata["childProjects"]

    return {
        "version": "1.0",
        "lastUpdated": datetime.now().strftime("%Y-%m-%d"),
        "projects": projects,
        "fixedTasks": ["和杨老师交流"],
    }


def main():
    output_path = DEFAULT_OUTPUT
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:]):
            if arg == "--output" and i + 2 < len(sys.argv):
                output_path = Path(sys.argv[i + 2])
            elif arg.startswith("--output="):
                output_path = Path(arg.split("=", 1)[1])

    data = scan_all()

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    n_projects = len(data["projects"])
    n_tasks = sum(len(p.get("incompleteTasks", [])) for p in data["projects"].values())
    print(
        f"缓存已更新: {n_projects} 个项目, {n_tasks} 个未完成任务 → {output_path}"
    )


if __name__ == "__main__":
    main()