class Translator:
    """Peforms the translation from VM -> ASM for one VM file"""

    def __init__(self, file_name):
        self.file_name = file_name
        self.label_counter = 0

    def get_unique_label(self, name):
        self.label_counter += 1
        return f"{self.file_name}.{name}.{self.label_counter}"

    def translate_push_cmd(self, segment, index):
        """Translates push command into asm"""
        segment_table = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }

        if segment == "constant":
            return [
                f"// push constant {index}",
                f"@{index}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ]
        if segment in segment_table:
            base = segment_table[segment]
            return [
                f"// push {segment} {index}",
                f"@{base}",
                "D=M",
                f"@{index}",
                "A=D+A",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ]
        if segment == "temp":
            addr = 5 + index
            return [
                "// push temp {index}",
                f"@{addr}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ]
        if segment == "pointer":
            base = "THIS" if index == 0 else "THAT"
            return [
                f"// push pointer {index}",
                f"@{base}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ]
        if segment == "static":
            return [
                f"// push static {index}",
                f"@{self.file_name}.{index}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ]

    def translate_pop_cmd(self, segment, index):
        """Translates pop command into asm"""
        segment_table = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT"
        }

        if segment in segment_table:
            base = segment_table[segment]
            return [
                f"// pop {segment} {index}",
                f"@{base}",
                "D=M",
                f"@{index}",
                "D=D+A",
                "@R13",  # We store the calculated address in R13
                "M=D",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "@R13",
                "A=M",
                "M=D"
            ]

        if segment == "temp":
            addr = 5 + index
            return [
                f"// pop temp {index}",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{addr}",
                "M=D"
            ]

        if segment == "pointer":
            base = "THIS" if index == 0 else "THAT"
            return [
                f"// pop pointer {index}",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{base}",
                "M=D"
            ]

        if segment == "static":
            return [
                f"// pop static {index}",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                f"@{self.file_name}.{index}",
                "M=D"
            ]

    def translate_logic_arithmetic_cmds(self, command):
        """Generate assembly code for arithmetic/logical commands."""
        if command == "add":
            return [
                "// add",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "A=A-1",
                "M=D+M"
            ]

        if command == "sub":
            return [
                "// sub",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "A=A-1",
                "M=M-D"
            ]

        if command == "neg":
            return [
                "// neg",
                "@SP",
                "A=M-1",
                "M=-M"
            ]

        if command in ["eq", "gt", "lt"]:
            jump_type = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
            true_label = self.get_unique_label("TRUE")
            false_label = self.get_unique_label("FALSE")

            return [
                f"// {command}",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "A=A-1",
                "D=M-D",
                f"@{true_label}",
                f"D;{jump_type}",
                "@SP",
                "A=M-1",
                "M=0",  # 0 is False
                f"@{false_label}",
                "0;JMP",
                f"({true_label})",
                "@SP",
                "A=M-1",
                "M=-1",  # -1 True
                f"({false_label})"
            ]

        if command == "and":
            return [
                "// and",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "A=A-1",
                "M=D&M"
            ]

        if command == "or":
            return [
                "// or",
                "@SP",
                "M=M-1",
                "A=M",
                "D=M",
                "A=A-1",
                "M=D|M"
            ]

        if command == "not":
            return [
                "// not",
                "@SP",
                "A=M-1",
                "M=!M"
            ]
