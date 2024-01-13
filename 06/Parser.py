"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = input_file.read().splitlines()
        self.current_command_idx = 0
        self.curr_command = None
        self.dest = None
        self.comp = None
        self.jump = None

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        return self.current_command_idx < len(self.input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        # Your code goes here!
        command_with_comments = self.input_lines[self.current_command_idx]
        # print(command_with_comments)
        # print(command_with_comments)
        self.curr_command = command_with_comments.split('//', 1)[0]. \
            replace(" ", "").strip().strip()  # remove whitespaces and comments
        # print(self.curr_command)

        self.current_command_idx += 1

    def command_type(self) -> str:  # with no symbolic references
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        # Your code goes here!

        if self.curr_command[0] == "@":
            return "A_COMMAND"
        elif self.curr_command[0] == "(":
            return "L_COMMAND"
        else:
            self.is_c_command(self.curr_command)
            return "C_COMMAND"


    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        # print(self.curr_command)
        if self.curr_command[0] == "@":
            return self.curr_command[1:]
        else:
            return self.curr_command[1:-1]

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """

        return self.dest

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self.comp

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self.jump

    def is_c_command(self, instruction):
        # Define lists of valid dest, comp, and jump mnemonics
        valid_dest = ["", "M", "D", "DM", "MD", "A", "AM", "AD", "ADM", "AMD"]
        valid_comp = [
            "0", "1", "-1", "D", "A", "!D", "!A", "-D",
            "-A", "D+1", "A+1", "D-1", "A-1", "D+A", "D-A",
            "A-D", "D&A", "D|A", "M", "!M", "-M", "M+1",
            "M-1", "D+M", "D-M", "M-D", "D&M", "D|M"
        ]
        valid_jump = ["", "JGT", "JEQ", "JGE", "JLT", "JNE", "JLE", "JMP"]

        # Split the instruction into dest, comp, and jump parts
        parts = instruction.split(";")
        if len(parts) == 2:
            dest_comp = parts[0]
            self.jump = parts[1]
        else:
            dest_comp = parts[0]
            self.jump = ""

        # Split the dest_comp part into dest and comp
        dest_comp_parts = dest_comp.split("=")
        if len(dest_comp_parts) == 2:
            self.dest = dest_comp_parts[0]
            self.comp = dest_comp_parts[1]
        else:
            self.dest = ""
            self.comp = dest_comp_parts[0]

        # Check if dest, comp, and jump are valid
        return self.dest in valid_dest and self.comp in valid_comp and self.jump in valid_jump

    def is_there_command(self):
        if self.curr_command == "":
            return False
        return True

    def reset(self) -> None:
        self.current_command_idx = 0


#write a function is_c_command that will say if a string is a c instruction