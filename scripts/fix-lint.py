#!/usr/bin/env python3
"""
Script para corrigir automaticamente problemas de lint comuns
"""

import os
import re


def remove_unused_imports(file_path):
    """Remove imports não utilizados baseado nos erros do flake8"""
    
    unused_patterns = {
        'pytest': ['pytest'],
        'asyncio': ['asyncio'],
        'pytest_asyncio': ['pytest_asyncio'], 
        'io': ['io'],
        'logging': ['logging'],
        'unittest.mock.AsyncMock': ['AsyncMock'],
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            should_remove = False
            
            # Check for unused imports
            for pattern, imports in unused_patterns.items():
                if any(f'import {imp}' in line and pattern in line for imp in imports):
                    # Only remove if it's a simple import line
                    if line.strip().startswith(('import ', 'from ')):
                        should_remove = True
                        modified = True
                        break
            
            if not should_remove:
                new_lines.append(line)
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✓ Removed unused imports from {file_path}")
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")


def remove_unused_variables(file_path):
    """Remove variáveis não utilizadas"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Remove unused variables by prefixing with underscore
        patterns = [
            (r'(\s+)([a-zA-Z_][a-zA-Z0-9_]*) = (.+?)  # F841', r'\1_\2 = \3'),
            (r'(\s+)user_no_scopes = (.+)', r'\1_ = \2  # user_no_scopes unused'),
            (r'(\s+)scope_validator = (.+)', r'\1_ = \2  # scope_validator unused'),
            (r'(\s+)ai_provider = (.+)', r'\1_ = \2  # ai_provider unused'),
            (r'(\s+)response = (.+)', r'\1_ = \2  # response unused'),
            (r'(\s+)cpu_before = (.+)', r'\1_ = \2  # cpu_before unused'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed unused variables in {file_path}")
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")


def remove_trailing_whitespace(file_path):
    """Remove espaços em branco desnecessários"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        modified = False
        new_lines = []
        
        for line in lines:
            # Remove trailing whitespace
            new_line = line.rstrip() + '\n'
            if new_line != line:
                modified = True
            new_lines.append(new_line)
        
        # Remove final newline if empty
        if new_lines and new_lines[-1].strip() == '':
            new_lines[-1] = new_lines[-1].rstrip()
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"✓ Removed trailing whitespace from {file_path}")
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")


def process_directory(directory):
    """Processa todos os arquivos Python em um diretório"""
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                remove_unused_imports(file_path)
                remove_unused_variables(file_path)
                remove_trailing_whitespace(file_path)


if __name__ == "__main__":
    directories = ['app', 'tests']
    files = ['main.py']
    
    print("🔧 Fixing lint issues...")
    
    for directory in directories:
        if os.path.exists(directory):
            process_directory(directory)
    
    for file in files:
        if os.path.exists(file):
            remove_unused_imports(file)
            remove_unused_variables(file)
            remove_trailing_whitespace(file)
    
    print("\n✅ Lint fixes completed!")
    print("Run 'black app/ tests/ main.py' and 'isort app/ tests/ main.py' to finish formatting")
