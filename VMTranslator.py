import os
import sys
from pathlib import Path
from Translator import Translator


def generate_bootstrap_asm():
    """
    Upon reset, the hack computer will fetch and execute the instruction located in ROM[0]
    Therefore we need to put some init code at the beginning of our generated asm
    """
    translator = Translator("bootstrap")
    return [
        "@256",
        "D=A",
        "@SP",
        "M=D",
        # We don't need to manually initialize LCL, ARG, THIS, and THAT before calling Sys.init because:
        # Any values in them will be saved onto the stack by translate_fn_call (The saved values are never used since Sys.init never returns!)
        # Call correctly sets up LCL and ARG
        *translator.translate_fn_call("Sys.init", 0)
    ]


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

    if command == "label":
        return translator.translate_label(parts[1])

    if command == "goto":
        return translator.translate_goto(parts[1])

    if command == "if-goto":
        return translator.translate_if_goto(parts[1])

    if command == "function":
        return translator.translate_fn_declaration(parts[1], int(parts[2]))

    if command == "call":
        return translator.translate_fn_call(parts[1], int(parts[2]))

    if command == "return":
        return translator.translate_fn_return()


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
    # asm_bootstrap = generate_bootstrap_asm()
    asm_commands = translate_vm_file(path)
    with open(path.with_suffix('.asm'), 'w', encoding='UTF-8') as f:
        # for bootstrap_command in asm_bootstrap:
        #     f.write(bootstrap_command + '\n')
        for command_list in asm_commands:
            f.write('\n'.join(command_list) + '\n')


def translate_directory(path):
    asm_bootstrap = generate_bootstrap_asm()
    dir_name = path.stem
    with open(path.joinpath(f"{dir_name}.asm"), 'w', encoding='UTF-8') as f:
        for bootstrap_command in asm_bootstrap:
            f.write(bootstrap_command + '\n')
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
