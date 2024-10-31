# Used to generate unique JMP labels
jump_counter = 0

def generate_push(segment, index, file_name):
    """Generate assembly code for push command."""
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

    elif segment in segment_table:
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

    elif segment == "temp":
        addr = 5 + index
        return [
            f"// push temp {index}",
            f"@{addr}",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]

    elif segment == "pointer":
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

    elif segment == "static":
        return [
            f"// push static {index}",
            f"@{file_name}.{index}",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]

    raise ValueError(f"Invalid segment: {segment}")


def generate_pop(segment, index, file_name):
    """Generate assembly code for pop command."""
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

    elif segment == "temp":
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

    elif segment == "pointer":
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

    elif segment == "static":
        return [
            f"// pop static {index}",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            f"@{file_name}.{index}",
            "M=D"
        ]

    raise ValueError(f"Invalid segment: {segment}")


def generate_arithmetic(command):
    """Generate assembly code for arithmetic/logical commands."""
    global jump_counter

    if command == "add":
        return [
            "// add",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "M=M+D"
        ]

    elif command == "sub":
        return [
            "// sub",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "M=M-D"
        ]

    elif command == "neg":
        return [
            "// neg",
            "@SP",
            "A=M-1",
            "M=-M"
        ]

    elif command in ["eq", "gt", "lt"]:
        jump_type = {"eq": "JEQ", "gt": "JGT", "lt": "JLT"}[command]
        current_count = jump_counter
        jump_counter += 1  # Increment counter for next use
        return [
            f"// {command}",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "D=M-D",
            f"@TRUE.{current_count}",
            f"D;{jump_type}",
            "@SP",
            "A=M-1",
            "M=0",  # 0 is False
            f"@CONTINUE.{current_count}",
            "0;JMP",
            f"(TRUE.{current_count})",
            "@SP",
            "A=M-1",
            "M=-1",  # -1 True
            f"(CONTINUE.{current_count})"
        ]

    elif command == "and":
        return [
            "// and",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "M=M&D"
        ]

    elif command == "or":
        return [
            "// or",
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "A=A-1",
            "M=M|D"
        ]

    elif command == "not":
        return [
            "// not",
            "@SP",
            "A=M-1",
            "M=!M"
        ]

    raise ValueError(f"Invalid arithmetic command: {command}")
