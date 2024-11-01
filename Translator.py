"""
According to Hack Machine Language Specification the following built in symbols exist
- SP points to RAM[0]
- LCL points to RAM[1]
- ARG points to RAM[2]
- THIS points to RAM[3]
- THAT poinst to RAM[4]
- R13,R14,R15 point to RAM[13,14,15]
"""


class Translator:
    """Peforms the translation from VM -> ASM for one VM file"""

    def __init__(self, file_name):
        self.file_name = file_name
        self.scope_fn_name = ""
        self.label_counter = 0
        self.call_counter = 0

    def get_unique_label(self, name):
        self.label_counter += 1
        return f"{self.file_name}.{name}.{self.label_counter}"

    def push_D_onto_stack(self):
        """
        Generates ASM to push the value of register D onto the stack
        """
        return [
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ]

    def translate_fn_declaration(self, name, nVars):
        """Translates function command into asm. Example: 'function Foo.test 2'
        - nVars specifies how many local variables the function has! (0,1,2,3 and so on)
        - function without any local variables would be specified as 'function Foo 0'
        """
        self.scope_fn_name = name
        asm = [f"// function {name} {nVars}"]
        # During a call we will jump into the translated fn declaration, therefore we need a label
        asm.extend([f"({name})"])
        # Right after the jump LCL = SP, we now have to make place for nVars in the LCL segment. We can simply do this by pushing 0 nVars onto the stack. This will also move the SP
        if nVars > 0:
            asm.extend(["D=0"])
            for _ in range(nVars):
                asm.extend(self.push_D_onto_stack())

        return asm
        # LCL now points correctly to the first LCL argument
        # SP now points right after the local arguments to the first free memory of the stack

    def translate_fn_call(self, name, nArgs):
        """Translates call command into asm. Example: call Bar.test 2
        - nArgs specifies how many arguments were pushed to the stack before the call
        - the compiler will have made sure that the nArgs have been pushed onto the stack before the call!
        """
        self.call_counter += 1
        asm = [f"// call {name} {nArgs}"]
        return_label = f"{self.scope_fn_name}${name}$ret.{self.call_counter}"

        # Step 1: Store Caller Frame
        # store return pointer on stack
        asm.extend([
            f"@{return_label}",
            "D=A",  # This will be the position of the return label in the generated asm code
            *self.push_D_onto_stack()
        ])

        # store caller LCL pointer on stack
        asm.extend([
            "@LCL",
            "D=M",
            *self.push_D_onto_stack()
        ])
        # store caller ARG pointer on stack
        asm.extend([
            "@ARG",
            "D=M",
            *self.push_D_onto_stack()
        ])
        # store caller THIS pointer on stack
        asm.extend([
            "@THIS",
            "D=M",
            *self.push_D_onto_stack()
        ])
        # store caller THAT pointer on stack
        asm.extend([
            "@THAT",
            "D=M",
            *self.push_D_onto_stack()
        ])

        # Step 2: Prepare Callee Frame

        # Set ARG to the first argument which is 5 + nArgs positions behind the current SP
        asm.extend([
            "@SP",
            "D=M",
            f"@{5+nArgs}",
            "D=D-A",
            "@ARG",
            "M=D"
        ])

        # Set LCL to where the SP now is (see fn declaration to understand how the LCL segment will be created and SP moved)
        asm.extend([
            "@SP",
            "D=M",
            "@LCL",
            "M=D"
        ])

        # Step 3: Jump into ASM code of called function
        asm.extend([
            f"@{name}",
            "0;JMP",
            f"({return_label})"
        ])

        return asm

    def translate_fn_return(self):
        """Terminates the current function and returns controls to the caller
        - return the top most value of the stack of the callee and replaces the arguments on the stack of the caller with this value
        Basically the caller will see after the call that the arguments on the stack have been replaced by the result of the call

        ! Important Implicit Rule: Callee has to push a value onto the stack before return! Job of the compiler! Topmost value is assumed to be the return value
        """

        asm = ["// return"]

        # LCL points to the first memory register of the current frame. The stored callers frame is right before it. We store this important pointer in R13
        # R13 = frame
        asm.extend([
            "@LCL",
            "D=M",
            "@R13",
            "M=D"
        ])
        # We store the return address in R14
        # return address = frame - 5
        asm.extend([
            "@R13",
            "D=M",
            "@5",
            "A=D-A",
            "D=M",
            "@R14",
            "M=D"
        ])
        # We replace argument[0] with the return value of the function which is assumed to be on top of the stack
        asm.extend([
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            "@ARG",
            "A=M",
            "M=D"
        ])
        # We recycle the callees stack by moving the SP right after argument[0] (caller assumes returned value on top of stack)
        asm.extend([
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D"
        ])

        # Restore THAT
        asm.extend([
            "@R13",
            "D=M",
            f"@{1}",
            "D=D-A",
            "A=D",
            "D=M",
            "@THAT",
            "M=D"
        ])

        # Restore THIS
        asm.extend([
            "@R13",
            "D=M",
            f"@{2}",
            "D=D-A",
            "A=D",
            "D=M",
            "@THIS",
            "M=D"
        ])

        # Restore ARG
        asm.extend([
            "@R13",
            "D=M",
            f"@{3}",
            "D=D-A",
            "A=D",
            "D=M",
            "@ARG",
            "M=D"
        ])

        # Restore LCL
        asm.extend([
            "@R13",
            "D=M",
            f"@{4}",
            "D=D-A",
            "A=D",
            "D=M",
            "@LCL",
            "M=D"
        ])

        # JMP to caller return address
        asm.extend([
            "@R14",
            "A=M",
            "0;JMP"
        ])

        return asm

    def translate_label(self, name):
        """Translates label command into asm"""
        return [
            f"// label {name}",
            f"({self.scope_fn_name}${name})"]

    def translate_goto(self, name):
        """Translates goto comamnd into asm"""
        return [
            f"// goto {name}",
            f"@{self.scope_fn_name}${name}",
            "0;JMP"
        ]

    def translate_if_goto(self, name):
        """translates if-goto command into asm"""
        return [
            f"// if-goto {name}",
            # pop comparison value from stack
            "@SP",
            "M=M-1",
            "A=M",
            "D=M",
            # goto if comparison value is true (not 0)
            f"@{self.scope_fn_name}${name}",
            "D;JNE"
        ]

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
