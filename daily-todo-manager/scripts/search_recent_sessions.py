#!/usr/bin/env python3
"""
跨会话用户消息搜索脚本 — 解决 Agent 只搜当前上下文、漏掉并行会话的问题

用法:
  python search_recent_sessions.py --days 7
  python search_recent_sessions.py --from 2026-05-21 --to 2026-05-25
  python search_recent_sessions.py --today      # 只搜今天
  python search_recent_sessions.py --yesterday  # 只搜昨天
  python search_recent_sessions.py --days 7 --transcript-dir /path/to/transcripts

输出: JSON 格式，按日期分组，每条包含 session_id / 时间 / 用户消息摘要 / 检测到的项目
"""
import json, os, sys, argparse, re
from datetime import datetime, timedelta, timezone
from pathlib import Path


def get_default_transcript_dir():
    """获取默认的 Claude Code 对话记录目录"""
    home = os.path.expanduser("~")
    return os.path.join(home, ".claude", "projects")


def get_default_projects_dir():
    """获取默认的 TODO 项目目录"""
    todo_dir = os.environ.get("TODO_DIR", "")
    if todo_dir:
        return os.path.join(todo_dir, "projects")
    return None


def load_project_keywords(projects_dir):
    """
    从项目文件名提取项目名关键词。
    每个项目自动生成关键词：项目名本身 + 文件名中的词语。
    如需自定义简称，在项目的 CLAUDE.md 中配置。
    """
    keywords = {}
    if not projects_dir or not os.path.isdir(projects_dir):
        return keywords

    for f in sorted(os.listdir(projects_dir)):
        if not f.endswith(".md"):
            continue
        fpath = os.path.join(projects_dir, f)
        stem = f.replace(".md", "")
        # 去掉日期前缀
        name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem)
        # 默认关键词：项目名本身
        keywords[name] = [name]

        # 尝试从文件头部读取自定义关键词
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"\*\*搜索关键词\*\*[：:]\s*(.+)", line)
                    if m:
                        extra = [k.strip() for k in m.group(1).split(",")]
                        keywords[name].extend(extra)
                        break
                    # 读到第一个 ## 就停止（只在元数据区找）
                    if line.startswith("##"):
                        break
        except Exception:
            pass

    return keywords


def extract_user_messages(filepath, date_from, date_to):
    """从 JSONL 文件提取指定日期范围内的用户消息"""
    messages = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if not (obj.get('type') == 'user' and
                            obj.get('message', {}).get('role') == 'user'):
                        continue
                    ts_str = obj.get('timestamp', '')
                    if not ts_str:
                        continue
                    ts_date = ts_str[:10]
                    if ts_date < date_from or ts_date > date_to:
                        continue

                    content = obj['message'].get('content', [])
                    text = ''
                    if isinstance(content, list):
                        for c in content:
                            if c.get('type') == 'text':
                                text = c['text']
                                break
                    if not text:
                        continue

                    # 过滤掉 skill 加载内容（太长的 SKILL.md 内容）
                    if text.startswith('Base directory for this skill:'):
                        continue
                    if '日周月待办联动管理系统' in text[:200]:
                        continue
                    # 过滤 tool_result 回传
                    if len(text) > 500:
                        text = text[:500] + '...'

                    messages.append({
                        'time': ts_str,
                        'text': text,
                        'session': obj.get('sessionId', '')[:8]
                    })
                except (json.JSONDecodeError, KeyError):
                    continue
    except Exception as e:
        print(f"  [WARN] Failed to read {filepath.name}: {e}", file=sys.stderr)
    return messages


def detect_projects(text, project_keywords):
    """根据消息文本检测涉及的项目"""
    hits = []
    text_lower = text.lower()
    for proj_name, kws in project_keywords.items():
        for kw in kws:
            if kw.lower() in text_lower:
                hits.append(proj_name)
                break
    return list(set(hits)) if hits else ['其他/临时']


def main():
    parser = argparse.ArgumentParser(description='搜索跨会话用户消息')
    parser.add_argument('--days', type=int, default=7, help='搜索最近N天 (默认7)')
    parser.add_argument('--from', dest='date_from', help='起始日期 YYYY-MM-DD')
    parser.add_argument('--to', dest='date_to', help='结束日期 YYYY-MM-DD')
    parser.add_argument('--today', action='store_true', help='只搜今天')
    parser.add_argument('--yesterday', action='store_true', help='只搜昨天')
    parser.add_argument('--transcript-dir', help='Claude Code 对话记录目录 (默认 ~/.claude/projects/)')
    parser.add_argument('--projects-dir', help='TODO projects 目录 (默认 $TODO_DIR/projects)')
    parser.add_argument('--json', action='store_true', help='输出原始 JSON (默认输出人类可读摘要)')
    args = parser.parse_args()

    # 确定日期范围
    now = datetime.now(timezone.utc)
    if args.today:
        date_from = date_to = now.strftime('%Y-%m-%d')
    elif args.yesterday:
        d = now - timedelta(days=1)
        date_from = date_to = d.strftime('%Y-%m-%d')
    elif args.date_from and args.date_to:
        date_from, date_to = args.date_from, args.date_to
    else:
        date_to = now.strftime('%Y-%m-%d')
        date_from = (now - timedelta(days=args.days)).strftime('%Y-%m-%d')

    transcript_dir = Path(args.transcript_dir or get_default_transcript_dir())
    projects_dir = args.projects_dir or get_default_projects_dir()

    if not transcript_dir.exists():
        print(json.dumps({"error": f"Transcript dir not found: {transcript_dir}",
                          "hint": "Use --transcript-dir to specify the path, or set CLAUDE_TRANSCRIPT_DIR env var"},
                         ensure_ascii=False))
        sys.exit(1)

    project_keywords = load_project_keywords(projects_dir) if projects_dir else {}

    # 收集所有 JSONL 文件（递归搜索子目录）
    all_files = sorted(
        [f for f in transcript_dir.rglob("*.jsonl")],
        key=lambda f: f.stat().st_mtime, reverse=True
    )

    # 只搜修改时间在范围内的文件
    cutoff_ts = (now - timedelta(days=args.days + 1)).timestamp()
    recent_files = [f for f in all_files if f.stat().st_mtime > cutoff_ts]

    # 提取消息
    all_messages = []
    for f in recent_files:
        msgs = extract_user_messages(f, date_from, date_to)
        all_messages.extend(msgs)

    # 按日期分组
    by_date = {}
    for msg in all_messages:
        d = msg['time'][:10]
        if d not in by_date:
            by_date[d] = []
        projs = detect_projects(msg['text'], project_keywords)
        by_date[d].append({
            'time': msg['time'],
            'session': msg['session'],
            'text': msg['text'],
            'projects': projs
        })

    if args.json:
        print(json.dumps({
            'date_range': {'from': date_from, 'to': date_to},
            'sessions_scanned': len(recent_files),
            'messages_found': len(all_messages),
            'by_date': {d: [{'time': m['time'], 'text': m['text'][:200], 'projects': m['projects']}
                           for m in msgs]
                       for d, msgs in sorted(by_date.items())}
        }, ensure_ascii=False, indent=2))
    else:
        # 人类可读输出
        print(f"=== 跨会话搜索: {date_from} ~ {date_to} ===")
        print(f"扫描 {len(recent_files)} 个会话文件, 找到 {len(all_messages)} 条用户消息\n")
        for d in sorted(by_date.keys()):
            msgs = by_date[d]
            projects_today = set()
            for m in msgs:
                projects_today.update(m['projects'])
            print(f"## {d} ({len(msgs)} 条消息) — 涉及项目: {', '.join(sorted(projects_today))}")
            for i, m in enumerate(msgs[:30]):  # 每天最多显示30条
                proj_tag = f"[{','.join(m['projects'])}]" if m['projects'] != ['其他/临时'] else ''
                text_preview = m['text'].replace('\n', ' ')[:150]
                print(f"  {i+1}. {proj_tag} {text_preview}")
            if len(msgs) > 30:
                print(f"  ... 还有 {len(msgs) - 30} 条消息")
            print()


if __name__ == '__main__':
    main()
