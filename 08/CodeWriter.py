"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.output_stream = output_stream
        self.file_name = None
        self.label_idx = 0
        self.curr_function = "null"  # "Xxx.foo"
        self.call_counter = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        # Your code goes here!
        # This function is useful when translating code that handles the
        # static segment. For example, in order to prevent collisions between two
        # .vm files which push/pop to the static segment, one can use the current
        # file's name in the assembly variable's name and thus differentiate between
        # static variables belonging to different files.
        # To avoid problems with Linux/Windows/MacOS differences with regards
        # to filenames and paths, you are advised to parse the filename in
        # the function "translate_file" in Main.py using python's os library,
        # For example, using code similar to:
        # input_filename, input_extension = os.path.splitext(os.path.basename(input_file.name))
        self.file_name = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes assembly code that is the translation of the given 
        arithmetic command. For the commands eq, lt, gt, you should correctly
        compare between all numbers our computer supports, and we define the
        value "true" to be -1, and "false" to be 0.

        Args:
            command (str): an arithmetic command.
        """
        self.output_stream.write(f"//{command}\n")
        unary_arithmetic_dict = \
            {"neg": "-M", "not": "!M", "shiftleft": "M<<", "shiftright": "M>>"}
        binary_arithmetic_dict = \
            {"add": "+D", "sub": "-D", "and": "&D", "or": "|D"}
        jump_conditions = {"lt": "D;JGT", "gt": "D;JLT", "eq": "D;JEQ"}
        # Your code goes here!
        if command in binary_arithmetic_dict.keys():
            self.output_stream.write \
                (f"@SP\nA=M-1\nD=M\nA=A-1\nM=M{binary_arithmetic_dict[command]}"  
                 f"\n@SP\nM=M-1\n")
        elif command in unary_arithmetic_dict.keys():
            self.output_stream.write(
                f"@SP\nA=M-1\nM={unary_arithmetic_dict[command]}\n")
        elif command in jump_conditions.keys():

            # check if second number is negative
            self.output_stream.write(
                f"@SP\nA=M-1\nD=M\n@SEC_NEGATIVE{self.label_idx}\n"
                f"D;JLT\n@SEC_POSITIVE{self.label_idx}\n"
                f"D;JGT\n@BOTH_SAME{self.label_idx}\n"
                f"0;JMP\n")
            # check if second number is positive (second is negative)
            self.output_stream.write(
                f"(SEC_NEGATIVE{self.label_idx})\n@SP\nA=M-1\n"
                f"A=A-1\nD=M\n@BOTH_SAME{self.label_idx}\n"
                f"D;JLE\n@DIFFERENT{self.label_idx}\nD;JGT\n")
            # check if second number is positive (second is positive)
            self.output_stream.write(
                f"(SEC_POSITIVE{self.label_idx})\n@SP\nA=M-1\n"
                f"A=A-1\nD=M\n@BOTH_SAME{self.label_idx}\n"
                f"D;JGE\n@DIFFERENT{self.label_idx}\nD;JLT\n")
            # different signs (could be overflow)
            self.output_stream.write(f"(DIFFERENT{self.label_idx})\n")
            if command in ["lt", "gt"]:
                self.output_stream.write(
                    f"@SP\nA=M-1\nD=M\n@TRUE{self.label_idx}\n"
                    f"{jump_conditions[command]}\n@FALSE{self.label_idx}\n"
                    f"0;JMP\n")
            else:
                self.output_stream.write(f"@FALSE{self.label_idx}\n0;JMP\n")

            # no overflow
            self.output_stream.write(
                f"(BOTH_SAME{self.label_idx})\n@SP\nA=M-1\nD=M\nA=A-1\nD=D-M\n@TRUE{self.label_idx}\n"
                f"{jump_conditions[command]}\n(FALSE{self.label_idx})\n@SP\nA=M-1\n"
                f"A=A-1\nM=0\n@END{self.label_idx}\n0;JMP\n(TRUE{self.label_idx})\n"
                f"@SP\nA=M-1\nA=A-1\nM=-1\n(END{self.label_idx})\n@SP\nM=M-1\n")

        self.label_idx += 1

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes assembly code that is the translation of the given 
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # Your code goes here!
        # Note: each reference to "static i" appearing in the file Xxx.vm should
        # be translated to the assembly symbol "Xxx.i". In the subsequent
        # assembly process, the Hack assembler will allocate these symbolic
        # variables to the RAM, starting at address 16.
        segment_dict = {
            "local": "@LCL\nD=M",
            "argument": "@ARG\nD=M",
            "this": "@THIS\nD=M",
            "that": "@THAT\nD=M",
            "temp": "@5\nD=A",
            "pointer": "@THIS\nD=A"
        }
        if command == "C_PUSH":
            self.output_stream.write(f"//push {segment} {index}\n")
            if segment == "constant":
                # print("cons")
                self.output_stream.write(
                    f"@{index}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            elif segment == "static":
                self.output_stream.write(
                    f"@{self.file_name}.{index}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
            else:
                self.output_stream.write(
                    f"{segment_dict[segment]}\n@{index}\nA=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")

        if command == "C_POP":
            self.output_stream.write(f"//pop {segment} {index}\n")
            if segment == "constant":
                self.output_stream.write(
                    f"@SP\nM=M-1\nA=M\nD=M\n@{index}\nM=D\n")
            if segment == "static":
                self.output_stream.write(
                    f"@SP\nM=M-1\nA=M\nD=M\n")
                # Store in static segment at the specified index
                self.output_stream.write(
                    f"@{self.file_name}.{index}\nM=D\n")
            else:
                self.output_stream.write(
                    f"{segment_dict[segment]}\n@{index}\nD=D+A\n@R13\nM=D\n@SP\n"
                    f"M=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n")

    def write_label(self, label: str) -> None:
        """Writes assembly code that affects the label command. 
        Let "Xxx.foo" be a function within the file Xxx.vm. The handling of
        each "label bar" command within "Xxx.foo" generates and injects the symbol
        "Xxx.foo$bar" into the assembly code stream.
        When translating "goto bar" and "if-goto bar" commands within "foo",
        the label "Xxx.foo$bar" must be used instead of "bar".

        Args:
            label (str): the label to write.
        """
        self.output_stream.write(f"//write label {label}\n")
        self.output_stream.write(
            f"({self.curr_function}${label})\n")

    def write_goto(self, label: str) -> None:
        """Writes assembly code that affects the goto command.

        Args:
            label (str): the label to go to.
        """
        self.output_stream.write(f"//write goto {label}\n")
        self.output_stream.write(
            f"@{self.curr_function}${label}\n0;JMP\n")

    def write_if(self, label: str) -> None:
        """Writes assembly code that affects the if-goto command. 

        Args:
            label (str): the label to go to.
        """
        # if the top of the stack is not false, jump
        self.output_stream.write(
            f"//write goto {label} if top of stack is not false\n")
        self.output_stream.write(f"@SP\nA=M-1\nD=M\n@SP\nM=M-1\n@"
                                 f"{self.curr_function}${label}\nD;JNE\n")

    def write_function(self, function_name: str, n_vars: int) -> None:
        """Writes assembly code that affects the function command. 
        The handling of each "function Xxx.foo" command within the file Xxx.vm
        generates and injects a symbol "Xxx.foo" into the assembly code stream,
        that labels the entry-point to the function's code.
        In the subsequent assembly process, the assembler translates this 
        symbol into the physical address where the function code starts.

        Args:
            function_name (str): the name of the function.
            n_vars (int): the number of local variables of the function.
        """

        # The pseudo-code of "function function_name n_vars" is:
        # (function_name)       // injects a function entry label into the code
        # repeat n_vars times:  // n_vars = number of local variables
        #   push constant 0     // initializes the local variables to 0
        self.output_stream.write(f"//writing function {function_name}\n")
        self.curr_function = function_name
        self.output_stream.write(f"({function_name})\n")
        for _ in range(n_vars):
            self.write_push_pop("C_PUSH", "constant", 0)

    def write_call(self, function_name: str, n_args: int) -> None:
        """Writes assembly code that affects the call command. 
        Let "Xxx.foo" be a function within the file Xxx.vm.
        The handling of each "call" command within Xxx.foo's code generates and
        injects a symbol "Xxx.foo$ret.i" into the assembly code stream, where
        "i" is a running integer (one such symbol is generated for each "call"
        command within "Xxx.foo").
        This symbol is used to mark the return address within the caller's 
        code. In the subsequent assembly process, the assembler translates this
        symbol into the physical memory address of the command immediately
        following the "call" command.

        Args:
            function_name (str): the name of the function to call.
            n_args (int): the number of arguments of the function.
        """
        # The pseudo-code of "call function_name n_args" is:
        # push return_address   // generates a label and pushes it to the stack
        # push LCL              // saves LCL of the caller
        # push ARG              // saves ARG of the caller
        # push THIS             // saves THIS of the caller
        # push THAT             // saves THAT of the caller
        # ARG = SP-5-n_args     // repositions ARG
        # LCL = SP              // repositions LCL
        # goto function_name    // transfers control to the callee
        # (return_address)      // injects the return address label into the code
        self.call_counter += 1
        self.output_stream.write(f"//writing call {function_name}\n")
        for_return_address = f"{self.curr_function}$ret.{self.call_counter}"
        # push label address to the stack
        self.output_stream.write(
            f"@{for_return_address}\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        elements_to_push = ["LCL", "ARG", "THIS", "THAT"]
        for elem in elements_to_push:
            self.output_stream.write(
                f"@{elem}\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n")
        self.output_stream.write("@SP\nD=M\n")
        # self.output_stream.write(f"@{n_args}\nD=A\n@5\nD=A-D\n@SP\nD=M-D\n@ARG\nM=D\n")  # ARG = SP-5-n_args
        for _ in range(n_args + 5):
            self.output_stream.write(f"D=D-1\n")
        self.output_stream.write(f"@ARG\nM=D\n")
        self.output_stream.write(f"@SP\nD=M\n@LCL\nM=D\n")  # LCL = SP
        self.output_stream.write(
            f"@{function_name}\n0;JMP\n")  # goto function_name
        # print(self.curr_function)
        # print("kkk")
        self.output_stream.write(
            f"({for_return_address})\n")  # (return_address)

    # Xxx.foo$bar

    def write_return(self) -> None:
        """Writes assembly code that affects the return command."""

        # The pseudo-code of "return" is:
        # frame = LCL                   // frame is a temporary variable
        # return_address = *(frame-5)   // puts the return address in a temp var
        # *ARG = pop()                  // repositions the return value for the caller
        # SP = ARG + 1                  // repositions SP for the caller
        # THAT = *(frame-1)             // restores THAT for the caller
        # THIS = *(frame-2)             // restores THIS for the caller
        # ARG = *(frame-3)              // restores ARG for the caller
        # LCL = *(frame-4)              // restores LCL for the caller
        # goto return_address           // go to the return address
        self.output_stream.write(f"//writing return\n")
        self.output_stream.write(f"@LCL\nD=M\n@frame\nM=D\n")  # frame = LCL
        self.output_stream.write(f"@5\nD=A\n@frame\nD=M-D\nA=D\nD=M\n@return_address\nM=D\n") # return_address = *(frame-5)
        self.write_push_pop("C_POP", "argument", 0) # *ARG = pop()
        self.output_stream.write(f"@ARG\nD=M\nD=D+1\n@SP\nM=D\n") # SP = ARG + 1
        self.output_stream.write(f"@frame\nD=M-1\nA=D\nD=M\n@THAT\nM=D\n") # THAT = *(frame-1)
        self.output_stream.write(f"@2\nD=A\n@frame\nD=M-D\nA=D\nD=M\n@THIS\nM=D\n") # THIS = *(frame-2)
        self.output_stream.write(f"@3\nD=A\n@frame\nD=M-D\nA=D\nD=M\n@ARG\nM=D\n")  # ARG = *(frame-3)
        self.output_stream.write(f"@4\nD=A\n@frame\nD=M-D\nA=D\nD=M\n@LCL\nM=D\n")  # LCL = *(frame-4)
        self.output_stream.write(f"@return_address\nA=M\n0;JMP\n") # goto return_address