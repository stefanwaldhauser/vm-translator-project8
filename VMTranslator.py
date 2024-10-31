import sys
from pathlib import Path
from CodeWriter import generate_arithmetic, generate_pop, generate_push


def get_paths(input_path):
    vm_path = Path(input_path)
    if not vm_path.suffix == '.vm':
        raise ValueError("Input file must be a .vm file")
    return vm_path, vm_path.with_suffix('.asm')


def translate_line(file_name, line):
    parts = line.split()
    command = parts[0]

    if command in {
        'add', 'sub', 'neg',
        'eq', 'gt', 'lt',
        'and', 'or', 'not'
    }:
        return generate_arithmetic(command)

    if command == "push":
        return generate_push(parts[1], int(parts[2]), file_name)

    if command == "pop":
        return generate_pop(parts[1], int(parts[2]), file_name)


def translate_vm_file(file_path):
    file_name = file_path.stem
    with open(file_path, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if line and not line.startswith('//'):
                yield translate_line(file_name, line)


def translate_file(input_path):
    try:
        vm_path, asm_path = get_paths(input_path)
        asm_commands = translate_vm_file(vm_path)

        with open(asm_path, 'w', encoding='UTF-8') as f:
            for command_list in asm_commands:
                f.write('\n'.join(command_list) + '\n')

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python VMTranslator.py <filename.vm>")
        sys.exit(1)

    translate_file(sys.argv[1])


if __name__ == "__main__":
    main()
