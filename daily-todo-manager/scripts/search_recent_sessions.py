#!/usr/bin/env python3
"""
跨会话用户消息提取脚本 — 只提取原始消息，不做项目归类。
项目归属由 AI Agent 根据消息内容+上下文判断，避免关键词误匹配。

用法:
  python search_recent_sessions.py --days 7
  python search_recent_sessions.py --from 2026-05-21 --to 2026-05-25
  python search_recent_sessions.py --today      # 只搜今天
  python search_recent_sessions.py --yesterday  # 只搜昨天

输出: 按日期分组，每条包含 session_id / 时间 / 用户消息文本。
       AI Agent 读取输出后，根据消息内容+项目上下文做归属判断。
"""
import json, os, sys, argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

TRANSCRIPT_DIR = Path(os.path.expandvars(
    r"C:\Users\29774\.claude\projects\g---20260426-claude----"
))


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

                    # 过滤 skill 加载内容
                    if text.startswith('Base directory for this skill:'):
                        continue
                    if '日周月待办联动管理系统' in text[:200]:
                        continue
                    # 截断过长消息
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


def main():
    parser = argparse.ArgumentParser(description='搜索跨会话用户消息（不做项目归类）')
    parser.add_argument('--days', type=int, default=7, help='搜索最近N天 (默认7)')
    parser.add_argument('--from', dest='date_from', help='起始日期 YYYY-MM-DD')
    parser.add_argument('--to', dest='date_to', help='结束日期 YYYY-MM-DD')
    parser.add_argument('--today', action='store_true', help='只搜今天')
    parser.add_argument('--yesterday', action='store_true', help='只搜昨天')
    parser.add_argument('--json', action='store_true', help='输出原始 JSON')
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

    if not TRANSCRIPT_DIR.exists():
        print(json.dumps({"error": "Transcript dir not found"}, ensure_ascii=False))
        sys.exit(1)

    # 收集所有 JSONL 文件
    all_files = sorted(
        [f for f in TRANSCRIPT_DIR.iterdir() if f.suffix == '.jsonl'],
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

    # 按日期分组（不做项目归类——由 AI Agent 判断）
    by_date = {}
    for msg in all_messages:
        d = msg['time'][:10]
        if d not in by_date:
            by_date[d] = []
        by_date[d].append({
            'time': msg['time'],
            'session': msg['session'],
            'text': msg['text']
        })

    if args.json:
        print(json.dumps({
            'date_range': {'from': date_from, 'to': date_to},
            'sessions_scanned': len(recent_files),
            'messages_found': len(all_messages),
            'by_date': {d: [{'time': m['time'], 'text': m['text'][:200]}
                           for m in msgs]
                       for d, msgs in sorted(by_date.items())}
        }, ensure_ascii=False, indent=2))
    else:
        print(f"=== 跨会话搜索: {date_from} ~ {date_to} ===")
        print(f"扫描 {len(recent_files)} 个会话文件, 找到 {len(all_messages)} 条用户消息")
        print(f"⚠️ 项目归属由 AI Agent 判断，脚本不做关键词匹配\n")
        for d in sorted(by_date.keys()):
            msgs = sorted(by_date[d], key=lambda m: m['time'])
            print(f"## {d} ({len(msgs)} 条消息)")
            for i, m in enumerate(msgs[:50]):
                # 转换为北京时间 (UTC+8)
                try:
                    ts = m['time']
                    if 'T' in ts:
                        hour = (int(ts[11:13]) + 8) % 24
                        time_str = f"{hour:02d}:{ts[14:16]}"
                    else:
                        time_str = ts[11:16] if len(ts) >= 16 else ''
                except:
                    time_str = ts[11:16] if len(ts) >= 16 else ''
                text_preview = m['text'].replace('\n', ' ')[:200]
                print(f"  {i+1}. [{time_str}] [{m['session']}] {text_preview}")
            if len(msgs) > 50:
                print(f"  ... 还有 {len(msgs) - 50} 条消息")
            print()


if __name__ == '__main__':
    main()
