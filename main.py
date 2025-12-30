#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import os
import argparse
from pathlib import Path


def extract_text_content(raw_data: str) -> str:
    """
    从TRPG主持人输出中提取最后一个完整的 <TEXT>...</TEXT> 内容。
    自动排除 thinking 中的干扰 <TEXT> token。
    """
    # 找到所有 <TEXT> 的起始位置
    starts = [m.start() for m in re.finditer(r'<TEXT>', raw_data, re.IGNORECASE)]
    
    if not starts:
        return ""  # 未找到，直接返回空
    
    # 取最后一个 <TEXT>
    last_start_pos = starts[-1]
    content_start = last_start_pos + len('<TEXT>')
    
    tail = raw_data[content_start:]
    end_match = re.search(r'</TEXT>', tail, re.IGNORECASE)
    
    if not end_match:
        return ""  # 没有闭合标签
    
    core_content = tail[:end_match.start()]
    
    # 清理开头常见的系统指令行
    core_content = re.sub(
        r'^\[遵守<optimize_input>.*now\s+start\s+writing\]\s*',
        '',
        core_content,
        flags=re.IGNORECASE
    )
    
    # 移除结尾的 <Options>...</Options> 块（纯小说版不需要玩家选项）
    core_content = re.sub(r'<Options>.*?</Options>', '', core_content, flags=re.DOTALL)
    
    # 将平行事件分隔符 <p align="center">◆ ◆ ◆</p> 转为横线
    core_content = re.sub(
        r'<p\s+align="center">\s*◆\s*◆\s*◆\s*</p>',
        '\n\n---\n\n',
        core_content,
        flags=re.IGNORECASE
    )
    
    return core_content.strip()


def process_log(
    input_file: str,
    story_output: str = "novel_story.md",
    raw_output: str = "novel_story_raw.md",
    skip_examples: bool = True
):
    """
    处理 .jsonl 日志文件，生成纯净小说版 + 原始全记录版
    """
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"找不到输入文件: {input_file}")

    story_lines = ["# 冒险记录 (纯净故事版)\n\n---\n\n"]
    raw_lines = ["# 冒险记录 (原始演算全记录)\n\n---\n\n"]

    with open(input_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                print(f"[警告] 第 {i} 行 JSON 解析失败，跳过")
                continue

            # 跳过聊天元数据
            if 'chat_metadata' in data:
                continue
            
            name = data.get('name', 'Unknown')
            mes = data.get('mes', '')
            is_user = data.get('is_user', False)

            # 可选：跳过系统提示范例消息
            if skip_examples and "「输出范例」" in mes and "<thinking>" in mes:
                continue

            # === 1. 原始全记录 ===
            role_label = "玩家" if is_user else "主持人"
            raw_lines.append(f"## {role_label}: {name} (Line {i})\n\n")
            raw_lines.append(f"{mes}\n\n---\n\n")

            # === 2. 纯净小说版 ===
            if is_user:
                # 玩家消息：人物卡用代码块，其他用引用
                if "基础信息" in mes and "姓名:" in mes:
                    story_lines.append(f"### ✦ 人物卡：{name}\n\n```yaml\n{mes}\n```\n\n---\n\n")
                else:
                    story_lines.append(f"> **{name}**：{mes}\n\n")
            else:
                # 主持人消息：只提取故事正文
                story_content = extract_text_content(mes)
                if story_content:
                    story_lines.append(f"{story_content}\n\n---\n\n")

    # 写入文件
    Path(story_output).write_text(''.join(story_lines), encoding='utf-8')
    Path(raw_output).write_text(''.join(raw_lines), encoding='utf-8')

    print("处理完成！")
    print(f"  纯净小说版 → {story_output}")
    print(f"  原始全记录 → {raw_output}")


def main():
    parser = argparse.ArgumentParser(
        description="将 TRPG AI 聊天记录 (.jsonl) 转换为纯净小说版 + 原始记录版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python convert_trpg_log.py chat.jsonl
  python convert_trpg_log.py "我的冒险.jsonl" -s "第一卷.md" -r "完整记录.md"
  python convert_trpg_log.py input.jsonl --no-skip-examples
        """
    )
    
    parser.add_argument(
        'input_file',
        help="输入的 .jsonl 聊天记录文件路径"
    )
    
    parser.add_argument(
        '-s', '--story-output',
        default="novel_story.md",
        help="输出的纯净小说版文件名（默认: novel_story.md）"
    )
    
    parser.add_argument(
        '-r', '--raw-output',
        default="novel_story_raw.md",
        help="输出的原始全记录文件名（默认: novel_story_raw.md）"
    )
    
    parser.add_argument(
        '--no-skip-examples',
        action='store_true',
        help="不跳过包含「输出范例」的系统消息（默认会跳过）"
    )
    
    args = parser.parse_args()
    
    try:
        process_log(
            input_file=args.input_file,
            story_output=args.story_output,
            raw_output=args.raw_output,
            skip_examples=not args.no_skip_examples
        )
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    main()