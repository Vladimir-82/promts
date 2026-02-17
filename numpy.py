#!/usr/bin/env python3
"""
Упрощенный скрипт для поиска импортов numpy
"""

import os
import re
from pathlib import Path


def find_numpy_imports():
    """Быстрый поиск импортов numpy"""

    project_root = Path.cwd()
    print(f"Поиск в: {project_root}")
    print("-" * 50)

    found = False

    for root, dirs, files in os.walk(project_root):
        # Исключаем .venv и другие ненужные директории
        dirs[:] = [d for d in dirs if d != '.venv' and d != '__pycache__' and not d.startswith('.')]

        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                        # Ищем импорты numpy
                        if re.search(r'^\s*(import|from)\s+numpy', content, re.MULTILINE):
                            rel_path = file_path.relative_to(project_root)
                            print(f"✓ {rel_path}")

                            # Показываем конкретные строки с импортами
                            lines = content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(r'^\s*(import|from)\s+numpy', line):
                                    print(f"  └─ строка {i}: {line.strip()}")

                            found = True

                except (UnicodeDecodeError, PermissionError):
                    continue

    if not found:
        print("Импорты numpy не найдены")


if __name__ == "__main__":
    find_numpy_imports()