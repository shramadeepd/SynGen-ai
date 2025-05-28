#!/usr/bin/env python3
"""
Quick fix for database connection issues
"""

import re

def fix_db_file():
    with open('/mnt/d/Coding/SynGen-ai/Backend/services/database/db.py', 'r') as f:
        content = f.read()
    
    # Replace async with patterns
    pattern = r'(\s+)async with \(await get_conn\(\)\) as conn:'
    
    # Find all matches and their context
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if 'async with (await get_conn())' in line:
            # Get indentation
            indent = len(line) - len(line.lstrip())
            spaces = ' ' * indent
            
            # Replace with proper connection handling
            fixed_lines.append(f'{spaces}conn = await get_conn()')
            fixed_lines.append(f'{spaces}try:')
            
            # Find the end of the async with block and add finally
            brace_count = 0
            j = i + 1
            
            # Add all lines in the block with extra indentation
            while j < len(lines):
                block_line = lines[j]
                
                # If it's the start of a new function or class, we've gone too far
                if (block_line.strip() and 
                    not block_line.startswith(' ') and 
                    ('def ' in block_line or 'class ' in block_line)):
                    break
                
                # If line is empty or has same/less indentation as original, we're done
                if (block_line.strip() == '' or 
                    (block_line.strip() and len(block_line) - len(block_line.lstrip()) <= indent)):
                    # Add finally block
                    fixed_lines.append(f'{spaces}finally:')
                    fixed_lines.append(f'{spaces}    await conn.close()')
                    fixed_lines.append(block_line)
                    i = j + 1
                    break
                
                # Add the line with proper indentation
                if block_line.strip():
                    fixed_lines.append('    ' + block_line)
                else:
                    fixed_lines.append(block_line)
                
                j += 1
            else:
                # Reached end of file
                fixed_lines.append(f'{spaces}finally:')
                fixed_lines.append(f'{spaces}    await conn.close()')
                i = j
        else:
            fixed_lines.append(line)
            i += 1
    
    # Write back
    with open('/mnt/d/Coding/SynGen-ai/Backend/services/database/db.py', 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Fixed database connections in db.py")

if __name__ == "__main__":
    fix_db_file()