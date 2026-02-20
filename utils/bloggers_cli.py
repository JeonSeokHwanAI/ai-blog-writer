#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
블로거 목록 CLI - 빠른 조회용
사용법: python utils/bloggers_cli.py [명령] [인자]

명령:
  all           전체 목록
  <키워드>      키워드 검색
  #<주제>       주제 필터
  @<ID>         ID로 검색
"""

import json
import sys
import io
from pathlib import Path

# Windows 콘솔 UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트 기준 경로
ROOT = Path(__file__).parent.parent
BLOGS_FILE = ROOT / "config" / "blogs.json"


def load_blogs():
    """blogs.json 로드"""
    with open(BLOGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def print_table(blogs_dict, title="블로그 목록"):
    """마크다운 표 출력"""
    print(f"\n## {title} ({len(blogs_dict)}개)\n")
    print("| # | ID | 블로그명 | 별명 | 설명 | 주제 |")
    print("|---|-----|----------|------|------|------|")

    for i, (blog_id, info) in enumerate(blogs_dict.items(), 1):
        name = info.get("name", "")
        nickname = info.get("nickname", "")
        desc = info.get("description", "")[:30]
        topic = info.get("topics", {}).get("main", "")
        print(f"| {i} | {blog_id} | {name} | {nickname} | {desc} | {topic} |")


def search_blogs(blogs, keyword):
    """키워드로 검색"""
    keyword = keyword.lower()
    result = {}

    for blog_id, info in blogs.items():
        # ID, name, nickname, description에서 검색
        searchable = f"{blog_id} {info.get('name', '')} {info.get('nickname', '')} {info.get('description', '')}".lower()
        if keyword in searchable:
            result[blog_id] = info

    return result


def filter_by_topic(blogs, topic):
    """주제로 필터"""
    topic = topic.lstrip("#")
    result = {}

    for blog_id, info in blogs.items():
        topics = info.get("topics", {})
        main = topics.get("main", "")
        subs = topics.get("sub", [])

        if topic in main or topic in " ".join(subs):
            result[blog_id] = info

    return result


def get_by_id(blogs, target_id):
    """ID로 검색"""
    target_id = target_id.lstrip("@")
    if target_id in blogs:
        return {target_id: blogs[target_id]}
    return {}


def main():
    blogs = load_blogs()

    if len(sys.argv) < 2 or sys.argv[1] == "all":
        print_table(blogs, "전체 목록")

    elif sys.argv[1].startswith("#"):
        topic = sys.argv[1]
        result = filter_by_topic(blogs, topic)
        print_table(result, f"주제: {topic}")

    elif sys.argv[1].startswith("@"):
        blog_id = sys.argv[1]
        result = get_by_id(blogs, blog_id)
        if result:
            print_table(result, f"ID: {blog_id}")
        else:
            print(f"❌ '{blog_id}' 없음")

    else:
        keyword = " ".join(sys.argv[1:])
        result = search_blogs(blogs, keyword)
        if result:
            print_table(result, f"검색: {keyword}")
        else:
            print(f"❌ '{keyword}' 검색 결과 없음")


if __name__ == "__main__":
    main()
