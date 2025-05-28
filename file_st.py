import os

# Configuration
EXCLUDE_DIRS = {'.venv', '.vscode', '.git', '__pycache__'}
EXCLUDE_FILES = {'.gitignore'}
OUTPUT_FILE = 'all_code_dump.txt'

def extract_python_code(base_path='.', output_file=OUTPUT_FILE):
    with open(output_file, 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(base_path):
            # Exclude unwanted directories in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file in EXCLUDE_FILES or not file.endswith('.py'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_path)

                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        out.write(f'# === File: {rel_path} ===\n')
                        out.write(code + '\n\n')
                except Exception as e:
                    out.write(f'# Could not read {rel_path}: {e}\n\n')

    print(f"✅ All code saved to '{output_file}'.")

if __name__ == '__main__':
    extract_python_code('.')
