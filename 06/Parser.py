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
        self.curr_command = command_with_comments.split('//', 1)[0]. \
            replace(" ", "").strip().strip()  # remove whitespaces and comments
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
        elif is_c_command(self.curr_command)[0]:
            return "C_COMMAND"
        else:
            return "L_COMMAND"  # dont know if this is correct

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        if self.curr_command[0] == "@":
            return self.curr_command[1:]
        else:
            return self.curr_command

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


    def is_c_command(self, string) -> bool:
        parts = string.split('=')
        # Check if there is exactly one '=' to separate dest from comp
        if len(parts) == 2:
            self.dest, comp_and_jump = parts
            # Further split comp_and_jump based on ';'
            comp_and_jump_parts = comp_and_jump.split(';')

            # Check if there is at most one ';'
            if len(comp_and_jump_parts) <= 2:
                self.comp = comp_and_jump_parts[0]
                # Check if there is a jump part (optional)
                self.jump = comp_and_jump_parts[1] if len(
                    comp_and_jump_parts) == 2 else None

                # Check if dest, comp, and jump (if present) are valid
                if self.dest and self.comp:
                    # Here, you can perform additional validation if needed
                    return True

        # If the format is not matched, return False
        return False
