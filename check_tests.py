import os
import sys

# Directorios a revisar
SRC_DIR = 'backend'
TEST_DIR = os.path.join(SRC_DIR, 'tests')

# Archivos a ignorar (puedes agregar más si lo necesitas)
IGNORED = {'__init__.py'}

def main():
    # Busca todos los archivos .py en backend/ (excepto tests/)
    src_files = []
    for root, _, files in os.walk(SRC_DIR):
        if TEST_DIR in root:
            continue
        for f in files:
            if f.endswith('.py') and f not in IGNORED:
                rel_path = os.path.relpath(os.path.join(root, f), SRC_DIR)
                src_files.append(rel_path)

    # Para cada archivo, busca su test correspondiente
    missing_tests = []
    for src in src_files:
        base = os.path.splitext(os.path.basename(src))[0]
        test_file = f'test_{base}.py'
        test_path = os.path.join(TEST_DIR, test_file)
        if not os.path.exists(test_path):
            missing_tests.append((src, test_path))

    if missing_tests:
        print("Faltan archivos de test para los siguientes módulos:")
        for src, test in missing_tests:
            print(f"  - {src} → debería tener: {test}")
        sys.exit(1)
    else:
        print("¡Todos los archivos tienen su test correspondiente!")

if __name__ == "__main__":
    main()