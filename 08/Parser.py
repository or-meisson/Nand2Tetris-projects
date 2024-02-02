"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    # Parser
    
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly 
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the lines end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that, 
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = list(
            filter(lambda x: len(x.strip()), input_file.read().splitlines()))
        self.current_command_idx = 0
        # self.curr_command = None
        self.command_type_string = ""
        self._arg1 = None
        self._arg2 = None
        self.clean_command = ""

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # Your code goes here!
        return self.current_command_idx < len(self.input_lines)

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        # Your code goes here!
        command_with_comments = self.input_lines[self.current_command_idx]
        self.clean_command = command_with_comments.split('//', 1)[0].rstrip()
        command_components = self.clean_command.split()
        if not self.is_there_command():
            self.current_command_idx += 1
        else:

            self.command_type_string = command_components[0]
            self._arg1 = command_components[1] if len(
                command_components) > 1 else command_components[0]
            self._arg2 = command_components[2] if len(
                command_components) > 2 else None
            self.current_command_idx += 1

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """

        if self.command_type_string == "push":
            return "C_PUSH"
        if self.command_type_string == "pop":
            return "C_POP"
        if self.command_type_string in ["add", "sub", "neg", "eq", "gt", "lt",
                                        "and", "or", "not"]:
            return "C_ARITHMETIC"
        if self.command_type_string == "function":
            return "C_FUNCTION"
        if self.command_type_string == "return":
            return "C_RETURN"
        if self.command_type_string == "call":
            return "C_CALL"
        if self.command_type_string == "goto":
            return "C_GOTO"
        if self.command_type_string == "label":
            return "C_LABEL"
        if self.command_type_string == "if-goto":
            return "C_IF"

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        # Your code goes here!
        return self._arg1

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        # Your code goes here!
        return self._arg2

    def is_there_command(self):
        if self.clean_command == "":
            return False
        return True
