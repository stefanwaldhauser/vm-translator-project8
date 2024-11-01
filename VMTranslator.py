import sys
from pathlib import Path
from Translator import Translator


def get_paths(input_path):
    vm_path = Path(input_path)
    if not vm_path.suffix == '.vm':
        raise ValueError("Input file must be a .vm file")
    return vm_path, vm_path.with_suffix('.asm')


def translate_line(translator, line):
    parts = line.split()
    command = parts[0]

    if command in {
        'add', 'sub', 'neg',
        'eq', 'gt', 'lt',
        'and', 'or', 'not'
    }:
        return translator.translate_logic_arithmetic_cmds(command)

    if command == "push":
        return translator.translate_push_cmd(parts[1], int(parts[2]))

    if command == "pop":
        return translator.translate_pop_cmd(parts[1], int(parts[2]))


def translate_vm_file(file_path):
    file_name = file_path.stem
    translator = Translator(file_name)

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if line and not line.startswith('//'):
                yield translate_line(translator, line)


def translate_single_file(path):
    asm_commands = translate_vm_file(path)
    with open(path.with_suffix('.asm'), 'w', encoding='UTF-8') as f:
        # ToDo: First write init code
        for command_list in asm_commands:
            f.write('\n'.join(command_list) + '\n')


def translate_directory(path):
    dir_name = path.stem
    with open(path.joinpath(f"{dir_name}.asm"), 'w', encoding='UTF-8') as f:
        # ToDo: First write init code
        for file_path in path.glob('*.vm'):
            f.write(f"//Translating {file_path.stem}" + '\n')
            asm_commands = translate_vm_file(file_path)
            for command_list in asm_commands:
                f.write('\n'.join(command_list) + '\n')


def main():
    # No path specified -> translator operates on current folder
    if len(sys.argv) == 1:
        path = Path(os.getcwd())
    # Path to a directory <Directory> specified -> Translate all .vm files inside of that directorty into a single <Directory>.asm file and place it in the directory
    else:
        path = Path(sys.argv[1])
     # Path to one <FileName>.vm file specified -> Translate to <FileName>.asm and place it next to the source
    if path.is_file():
        translate_single_file(path)
    else:
        translate_directory(path)


if __name__ == "__main__":
    main()
