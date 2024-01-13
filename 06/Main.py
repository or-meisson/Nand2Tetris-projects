"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    # A good place to start is to initialize a new Parser object:

    symbol_table = SymbolTable()
    line_number = 0
    # first pass
    first_pass_parser = Parser(input_file)
    while first_pass_parser.has_more_commands():
        first_pass_parser.advance()
        if first_pass_parser.is_there_command():
            # print(first_pass_parser.curr_command)
            command_type = first_pass_parser.command_type()

            if command_type == "L_COMMAND":
                symbol = first_pass_parser.symbol()
                if not symbol_table.contains(symbol):
                    symbol_table.add_entry(symbol, line_number)
            elif command_type == "C_COMMAND" or command_type == "A_COMMAND":
                line_number += 1
    # for key, value in symbol_table.my_symbol_table.items():
    #     print(f"{key}: {value}")

    input_file.seek(0)
    # second pass
    empty_ram_space = 16
    second_pass_parser = Parser(input_file)
    while second_pass_parser.has_more_commands():
        second_pass_parser.advance()
        if second_pass_parser.is_there_command():
            # print(1)

            command_type = second_pass_parser.command_type()
            # print(command_type)
            if command_type == "A_COMMAND":
                symbol = second_pass_parser.symbol()
                # print(symbol)
                if not symbol.isdigit():
                    # print('not int')
                    if symbol_table.contains(symbol):
                        # print("contains")
                        address = symbol_table.my_symbol_table.get(symbol)
                        # print(address)
                        binary_representation = bin(address)[2:]
                        padded_binary = binary_representation.zfill(16)
                        # print("prints A")
                        output_file.write(f"{padded_binary}\n")
                    else:
                        # print("not contains")
                        symbol_table.add_entry(symbol, empty_ram_space)
                        binary_representation = bin(empty_ram_space)[2:]
                        padded_binary = binary_representation.zfill(16)
                        output_file.write(f"{padded_binary}\n")
                        empty_ram_space += 1
                else:
                    binary_representation = bin(int(symbol))[2:]
                    padded_binary = binary_representation.zfill(16)
                    output_file.write(f"{padded_binary}\n")

            # elif command_type == "L_COMMAND":
            #     symbol = second_pass_parser.symbol()
            #     address = symbol_table.my_symbol_table.get(symbol)
            #     binary_representation = bin(address)[2:]
            #     padded_binary = binary_representation.zfill(16)
            #     output_file.write(f"{padded_binary}\n")

            elif command_type == "C_COMMAND":
                dest = second_pass_parser.dest
                comp = second_pass_parser.comp
                jump = second_pass_parser.jump
                code = Code()
                binary_dest = code.dest(dest)
                binary_comp = code.comp(comp)
                binary_jump = code.jump(jump)
                # print(second_pass_parser.curr_command)
                if "<" in second_pass_parser.curr_command or ">" in \
                        second_pass_parser.curr_command:
                    output_file.write(
                        f"101{binary_comp}{binary_dest}{binary_jump}\n")
                else:
                    output_file.write(
                        f"111{binary_comp}{binary_dest}{binary_jump}\n")

    # Note that you can write to output_file like so:
    # output_file.write("Hello world! \n")


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
