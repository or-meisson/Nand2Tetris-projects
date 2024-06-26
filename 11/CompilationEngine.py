"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from SymbolTable import SymbolTable
from VMWriter import VMWriter


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        # self.all_methods = []
        self.what_to_return = None
        self.class_name = None
        self.tokenizer = input_stream
        self.output_stream = output_stream
        self.binary_ops = ["+", "-", "*", "/", "&", "|",
                           "<", ">", "="]
        self.lexical_elements_dict = {"KEYWORD": 'keyword',
                                      "IDENTIFIER": 'identifier',
                                      "SYMBOL": 'symbol',
                                      "INT_CONST": 'integerConstant',
                                      "STRING_CONST": 'stringConstant'
                                      }
        self.class_symbol_table = SymbolTable()
        self.subroutine_symbol_table = SymbolTable()
        self.vm_writer = VMWriter(output_stream)
        self.binary_operators_dict = {"+": "add", "-": "sub",
                                      "*": "call Math.multiply 2",
                                      "/": "call Math.divide 2", "&": "and",
                                      "|": "or",
                                      "<": "lt", ">": "gt", "=": "eq"}
        self.unary_operators_dict = {"-": "neg", "~": "not", "#": "shiftright",
                                     "^": "shiftleft"}
        self.kinds_dict = {"field": "this", "static": "static",
                           "arg": "argument",
                           "var": "local"}  # todo check if this is correct
        self.label_counter = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        # self.output_stream.write("<class>\n")
        self.tokenizer.advance()
        # print(self.tokenizer.current_token)
        self.process(["class"])
        self.class_name = self.tokenizer.current_token
        self.process([], True)
        self.process(["{"])
        while self.tokenizer.has_more_tokens():
            if self.tokenizer.current_token in ["static", "field"]:
                self.compile_class_var_dec()

            elif self.tokenizer.current_token in ["constructor", "function",
                                                  "method"]:
                # print("current func" + self.tokenizer.current_token)

                self.compile_subroutine()

        self.process(["}"], False, True)
        # self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        kind = self.tokenizer.current_token
        self.process(["static", "field"])
        type_ = self.tokenizer.current_token
        self.process(["boolean", "int", "char"], True)
        self.commas_while_loop(kind, type_, True)

    def commas_while_loop(self, kind, type_, is_class) -> None:  # maybe it was here
        name = self.tokenizer.current_token
        self.process([], True)  # the vars name
        # print(kind)
        if is_class:
            self.class_symbol_table.define(name, type_, kind)
            while self.tokenizer.current_token == ",":
                self.process([","])
                name = self.tokenizer.current_token
                self.process([], True)
                self.class_symbol_table.define(name, type_, kind)
        else:
            self.subroutine_symbol_table.define(name, type_, kind)
            while self.tokenizer.current_token == ",":
                self.process([","])
                name = self.tokenizer.current_token
                self.process([], True)
                self.subroutine_symbol_table.define(name, type_, kind)

        self.process([";"])

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        # self.output_stream.write("<subroutineDec>\n")
        self.subroutine_symbol_table.start_subroutine()
        subroutine_type = self.tokenizer.current_token
        # print(subroutine_type)
        self.process(["constructor", "function", "method"])

        self.what_to_return = self.tokenizer.current_token
        self.process(["void", "int", "char", "boolean"], True)
        name = self.tokenizer.current_token
        self.process([], True)
        self.process(["("])
        # print("hello")
        if subroutine_type == "function":
            # self.output_stream.write("function ")

            self.compile_parameter_list()
            self.process([")"])
            self.process(["{"])

            while self.tokenizer.current_token == "var":
                self.compile_var_dec()
            # self.output_stream.write("what ")
            local_vars = self.subroutine_symbol_table.var_count(
                "VAR")  # todo check if this is correct
            # print(local_vars)
            # print(f"{self.class_name}.{name}")

            self.vm_writer.write_function(f"{self.class_name}.{name}",
                                          local_vars)
            # self.vm_writer.write_function(name, local_vars)
            # self.output_stream.write("what is this")
            self.compile_statements()

            self.process(["}"])
        if subroutine_type == "method":

            self.subroutine_symbol_table.define("this", self.class_name, "arg")
            self.compile_parameter_list()
            self.process([")"])
            # self.compile_subroutine_body()
            self.process("{")

            while self.tokenizer.current_token == "var":
                self.compile_var_dec()
            local_vars = self.subroutine_symbol_table.var_count(
                "VAR")  # todo check if this is correct
            self.vm_writer.write_function(f"{self.class_name}.{name}",
                                          local_vars)
            self.vm_writer.write_push("argument", 0)
            self.vm_writer.write_pop("pointer", 0)
            self.compile_statements()
            self.process(["}"])
            # self.all_methods.append(name)

        if subroutine_type == "constructor":

            local_var = self.class_symbol_table.var_count(
                "VAR")  # todo check if this is correct
            self.vm_writer.write_function(f"{self.class_name}.{name}",
                                          local_var)
            self.vm_writer.write_push("constant",
                                      self.class_symbol_table.var_count(
                                          "FIELD"))
            self.compile_parameter_list()
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("pointer", 0)
            self.process([")"])
            self.process(["{"])
            # n_fields = self.class_symbol_table.var_count("FIELD")
            # self.vm_writer.write_push("constant", n_fields)

            while self.tokenizer.current_token == "var":
                self.compile_var_dec()
            self.compile_statements()
            # print(self.tokenizer.current_token)
            self.process(["}"])
            self.vm_writer.write_push("pointer", 0)
            # print("im here!")

            # self.vm_writer.write_return()  # todo check if this is correct

        # self.output_stream.write("</subroutineDec>\n")

    def compile_subroutine_body(self):
        self.process(["{"])
        while self.tokenizer.current_token == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.process(["}"])

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!

        if self.tokenizer.current_token == ")":
            return
        else:
            type_ = self.tokenizer.current_token
            self.process(["boolean", "int", "char"], True)
            name = self.tokenizer.current_token
            self.process([], True)
            self.subroutine_symbol_table.define(name, type_, "arg")
            while self.tokenizer.current_token == ",":
                self.process([","])
                type_ = self.tokenizer.current_token
                self.process(["boolean", "int", "char"], True)
                name = self.tokenizer.current_token
                self.process([], True)
                self.subroutine_symbol_table.define(name, type_, "arg")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!

        kind = self.tokenizer.current_token

        self.process(["var"])
        type_ = self.tokenizer.current_token
        self.process(["boolean", "int", "char"], True)

        self.commas_while_loop(kind, type_, False)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        while self.tokenizer.current_token in ["do", "let", "while",
                                               "return", "if"]:
            if self.tokenizer.current_token == "let":
                self.compile_let()
            elif self.tokenizer.current_token == "if":
                self.compile_if()
            elif self.tokenizer.current_token == "do":
                self.compile_do()
            elif self.tokenizer.current_token == "return":
                self.compile_return()
            elif self.tokenizer.current_token == "while":
                self.compile_while()

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.process(["do"])
        # self.output_stream.write("<doStatement>\n")
        name = self.tokenizer.current_token  # todo i think it is a name?
        self.process([], True)
        self.compile_subroutine_call(name)  # todo change to expression?
        self.vm_writer.write_pop("temp", 0)

        self.process([";"])

    def compile_let(self) -> None:  # todo got it from here
        """Compiles a let statement."""
        # Your code goes here!
        self.process(["let"])
        name = self.tokenizer.current_token
        # print(name)
        self.process([], True)
        # self.output_stream.write("<letStatement>\n")

        # check if it is an array
        if self.tokenizer.current_token == "[":
            try:
                self.vm_writer.write_push(
                    self.kinds_dict[
                        self.subroutine_symbol_table.kind_of(name)],
                    self.subroutine_symbol_table.index_of(name))
            except:
                #todo maybe problem here pong
                self.vm_writer.write_push(
                    self.kinds_dict[self.class_symbol_table.kind_of(name)],
                    self.class_symbol_table.index_of(name))

            self.process(["["])
            self.compile_expression()

            self.vm_writer.write_arithmetic("add")
            self.process(["]"])
            self.process(["="])
            self.compile_expression()
            self.vm_writer.write_pop("temp", 0)
            self.vm_writer.write_pop("pointer", 1)
            self.vm_writer.write_push("temp", 0)
            self.vm_writer.write_pop("that", 0)
        else:

            # try:  # check if in the subroutine table
            #     self.vm_writer.write_pop(self.kinds_dict[
            #                                  self.subroutine_symbol_table.kind_of(
            #                                      name)],
            #                              self.subroutine_symbol_table.index_of(
            #                                  name))  # todo is this the right dict?
            # except:  # if not in the subroutine table, it is in the class table
            #     self.vm_writer.write_pop(
            #         self.kinds_dict[self.class_symbol_table.kind_of(name)],
            #         self.class_symbol_table.index_of(name))

            # self.output_stream.write("<letStatement>\n")
            self.process(["="])
            self.compile_expression()
            # self.output_stream.write("pop down here\n")
            # print(name)
            # print(self.class_symbol_table.my_symbol_table)
            # print(self.subroutine_symbol_table.my_symbol_table)
            try:  # check if in the subroutine table
                self.vm_writer.write_pop(
                    self.kinds_dict[
                        self.subroutine_symbol_table.kind_of(name)],
                    self.subroutine_symbol_table.index_of(
                        name))  # todo is this the right dict?
            except:  # if not in the subroutine table, it is in the class table
                # # self.output_stream.write("gere\n")
                # print("hi")
                # print(self.class_symbol_table.kind_of(name))
                # print(self.kinds_dict[self.class_symbol_table.kind_of(name)])
                self.vm_writer.write_pop(
                    self.kinds_dict[self.class_symbol_table.kind_of(name)],
                    self.class_symbol_table.index_of(name))
            # self.output_stream.write("pop up here\n")
        # self.output_stream.write("</letStatement>\n")
        self.process([";"])
        # print("gets here")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        label_counter = self.label_counter  # save it won't change
        self.process(["while"])
        self.vm_writer.write_label(
            f"{self.class_name}.label1.{label_counter}")

        self.process(["("])
        self.compile_expression()
        self.process([")"])

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(
            f"{self.class_name}.label2.{label_counter}")

        self.process(["{"])
        self.compile_statements()
        self.process(["}"])

        self.vm_writer.write_goto(
            f"{self.class_name}.label1.{label_counter}")
        self.vm_writer.write_label(
            f"{self.class_name}.label2.{label_counter}")
        self.label_counter += 1

    def process(self, strings, is_identifier=False, is_last=False):
        if self.tokenizer.current_token not in strings and not is_identifier:
            print("syntax error")
        if not is_last:
            self.tokenizer.advance()

    # def print_xml_token(self):
    #     if self.tokenizer.token_type() in ["KEYWORD", "IDENTIFIER",
    #                                        "INT_CONST", "STRING_CONST"]:
    #         self.output_stream.write \
    #             (f"<{self.lexical_elements_dict[self.tokenizer.token_type()]}>"
    #              f" {self.tokenizer.current_token}"
    #              f" </{self.lexical_elements_dict[self.tokenizer.token_type()]}>\n")
    #     elif self.tokenizer.token_type() == "SYMBOL":
    #         self.output_stream.write \
    #             (f"<{self.lexical_elements_dict[self.tokenizer.token_type()]}>"
    #              f" {self.tokenizer.symbol()}"
    #              f" </{self.lexical_elements_dict[self.tokenizer.token_type()]}>\n")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!

        self.process(["return"])
        if self.tokenizer.current_token != ";":
            self.compile_expression()
        if self.what_to_return == "void":
            self.vm_writer.write_push("constant", 0)
        self.vm_writer.write_return()
        self.process([";"])

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        label_counter = self.label_counter  # save it won't change
        self.process(["if"])
        self.process(["("])
        self.compile_expression()
        self.process([")"])

        self.vm_writer.write_arithmetic("not")
        self.vm_writer.write_if(
            f"{self.class_name}.label1.{label_counter}")

        self.process(["{"])
        self.compile_statements()
        self.process(["}"])

        self.vm_writer.write_goto(
            f"{self.class_name}.label2.{label_counter}")
        self.vm_writer.write_label(
            f"{self.class_name}.label1.{label_counter}")

        if self.tokenizer.current_token == "else":
            self.process(["else"])

            self.process(["{"])
            self.compile_statements()
            self.process(["}"])

        self.vm_writer.write_label(
            f"{self.class_name}.label2.{label_counter}")
        self.label_counter += 1

    def compile_expression(self) -> None:  # expression
        """Compiles an expression."""
        # Your code goes here!
        # self.output_stream.write("<expression>\n")
        # print(self.tokenizer.current_token)
        self.compile_term()
        while self.tokenizer.current_token in self.binary_ops:
            # print(self.tokenizer.current_token)
            current_operator = self.tokenizer.current_token
            self.compile_op()
            self.compile_term()
            # print(self.binary_operators_dict[current_operator])
            self.vm_writer.write_arithmetic(
                self.binary_operators_dict[current_operator])

    def compile_term(self) -> None:  # expression
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """

        if self.tokenizer.token_type() == "INT_CONST":  # constant c
            # print("int const")
            self.vm_writer.write_push("constant", self.tokenizer.current_token)
            self.process([], True)
            # print(self.tokenizer.current_token)


        elif self.tokenizer.token_type() == "STRING_CONST":  # string c
            self.compile_string_const()


        elif self.tokenizer.current_token == "this":
            self.process([], True)
            self.vm_writer.write_push("pointer", 0)
        elif self.tokenizer.current_token in ["false", "null"]:
            self.process([], True)
            self.vm_writer.write_push("constant", 0)
        elif self.tokenizer.current_token == "true":
            self.process([], True)
            self.vm_writer.write_push("constant", 1)
            self.vm_writer.write_arithmetic("neg")



        elif self.tokenizer.current_token in ["-", "~", "^", "#"]:
            current_operator = self.tokenizer.current_token
            self.compile_unary_op()
            self.compile_term()
            self.vm_writer.write_arithmetic(
                self.unary_operators_dict[current_operator])




        # elif self.tokenizer.current_token == "(":
        #     self.process(["("])
        #     self.compile_expression()
        #     self.process([")"])

        # todo arrays and subroutine calls
        elif self.tokenizer.token_type() == "IDENTIFIER":  # varName
            # print("blabla")
            #
            # print(self.tokenizer.current_token)
            # print("blabla")
            name = self.tokenizer.current_token
            self.process([], True)

            if self.tokenizer.current_token == "[":  # varName[expression] - arrays
                self.process(["["])
                try:#todo maybe problem is here pong
                    self.vm_writer.write_push(self.kinds_dict
                                              [self.subroutine_symbol_table.kind_of(name)],
                                       self.subroutine_symbol_table.index_of(name))
                except:
                    self.vm_writer.write_push(self.kinds_dict
                                              [self.class_symbol_table.kind_of(name)],
                                       self.class_symbol_table.index_of(name))
                self.compile_expression()
                self.vm_writer.write_arithmetic("add")
                self.vm_writer.write_pop("pointer", 1)
                self.vm_writer.write_push("that", 0)
                self.process(["]"])


            elif self.tokenizer.current_token == ".":  # subroutine call
                self.compile_subroutine_call(name)


            elif self.tokenizer.current_token == "(":  # subroutine call
                self.compile_subroutine_call(name)

            else:  # end of term

                try:
                    # print("gets here!")
                    # print(name)
                    #todo maybe problem is here pong
                    self.vm_writer.write_push(self.kinds_dict
                                              [
                                                  self.subroutine_symbol_table.kind_of(
                                                      name)],
                                              self.subroutine_symbol_table.index_of(
                                                  name))
                except:
                    self.vm_writer.write_push(self.kinds_dict
                                              [self.class_symbol_table.kind_of(
                            name)],
                                              self.class_symbol_table.index_of(
                                                  name))


        # check if there are parentheses in the term
        elif self.tokenizer.current_token == "(":
            self.process(["("])
            self.compile_expression()
            self.process([")"])
        # print("im here!")

    def compile_expression_list(self) -> int:  # expression
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!

        if self.tokenizer.current_token == ")":
            return 0
        # print("im here!")
        self.compile_expression()
        counter = 1
        while self.tokenizer.current_token == ",":
            self.process([","])
            self.compile_expression()
            counter += 1
        return counter

    def compile_op(self) -> None:
        self.process(["+", "-", "*", "/", "&", "|", "<", ">", "="])

    def compile_unary_op(self) -> None:
        self.process(["-", "~", "^", "#"])

    def compile_subroutine_call(self, name: str) -> None:
        # name = self.tokenizer.current_token //todo maybe change to this?
        # print(name)
        # print(self.tokenizer.current_token)
        if self.tokenizer.current_token == "(":

            self.process(["("])
            self.vm_writer.write_push("pointer", 0)
            args = self.compile_expression_list()
            args += 1
            self.vm_writer.write_call(f"{self.class_name}.{name}", args)
            # self.process([")"])

        # self.kinds_dict[self.subroutine_symbol_table.kind_of(name)],
        # self.subroutine_symbol_table.index_of(
        #     name))

        else:

            self.process(['.'])
            subroutine_name = self.tokenizer.current_token
            # print(subroutine_name)
            self.process([], True)
            self.process(["("])
            # print(self.tokenizer.current_token)

            # func_name = self.tokenizer.current_token
            # subroutine_name = subroutine_name + "." + func_name
            # check if the function is a method or a function
            # self.output_stream.write("problem here?\n")
            # print(self.subroutine_symbol_table.my_symbol_table)
            # print(self.class_symbol_table.my_symbol_table)
            # print(name)
            try: #todo maybe problem is here pong
                # self.subroutine_symbol_table.my_symbol_table:
                self.vm_writer.write_push \
                    (self.kinds_dict[
                         self.subroutine_symbol_table.kind_of(name)],
                     self.subroutine_symbol_table.index_of(name))
                args = self.compile_expression_list()
                args += 1
                self.vm_writer.write_call(
                    f"{self.subroutine_symbol_table.type_of(name)}."
                    f"{subroutine_name}", args)
            # except:
            #     # self.class_symbol_table.my_symbol_table:
            #     self.vm_writer.write_push \
            #         (self.kinds_dict[
            #              self.class_symbol_table.kind_of(name)],
            #          self.class_symbol_table.index_of(name))
            #     args = self.compile_expression_list()
            #     args += 1
            #     self.vm_writer.write_call(
            #         f"{self.class_symbol_table.type_of(name)}."
            #         f"{subroutine_name}", args)
            except:
                # self.output_stream.write("problem here?\n")
                # print(self.tokenizer.current_token)
                args = self.compile_expression_list()
                # print(args)

                self.vm_writer.write_call(f"{name}.{subroutine_name}", args)
        # print(self.tokenizer.current_token)
        self.process([")"])
        # print("got here")

    def compile_string_const(self):
        string_length = len(self.tokenizer.current_token)
        self.vm_writer.write_push("constant", string_length)
        self.vm_writer.write_call("String.new", 1)
        for char in self.tokenizer.current_token:
            self.vm_writer.write_push("constant", ord(char))
            self.vm_writer.write_call("String.appendChar", 2)
        self.process([], True)
