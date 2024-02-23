"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


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
        self.tokenizer = input_stream
        self.output_stream = output_stream
        self. lexical_elements_dict = {"KEYWORD": 'keyword', "SYMBOL": 'symbol',
                          "IDENTIFIER": 'identifier',
                          "INT_CONST": 'integerConstant',
                          "STRING_CONST": 'stringConstant'}




    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.output_stream.write("<class>\n")
        self.process(["class"])
        self.process([], True)
        self.process(["{"])
        self.compile_class_var_dec()






    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        self.output_stream.write("<classVarDec>\n")
        self.process(["static", "field"])
        self.process(["int", "char", "boolean"])
        self.process([], True) #the vars name
        while self.tokenizer.curr_token == ",":
            self.process([","])
            self.process([], True)
        self.process([";"])
        self.output_stream.write("</classVarDec>\n")







    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        self.output_stream.write("<subroutineDec>\n")
        self.process(["constructor", "function", "method"])
        self.process(["void", "int", "char", "boolean"])
        self.process([], True)
        self.process(["("])
        self.compile_parameter_list()
        self.process([")"])
        self.output_stream.write("<subroutineBody>\n")
        self.process(["{"])
        while self.tokenizer.current_token == "var":
            self.compile_var_dec()
        self.compile_statements()
        self.process(["}"])
        self.output_stream.write("</subroutineBody>\n")
        self.output_stream.write("</subroutineDec>\n")










    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        self.output_stream.write("<parameterList>\n")
        self.process(["int", "char", "boolean"])
        self.process([], True)
        while self.tokenizer.current_token == ",":
            self.process([","])
            self.process(["int", "char", "boolean"])
            self.process([], True)
        self.output_stream.write("</parameterList>\n")






    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        self.output_stream.write("<varDec>\n")
        self.process(["var"])
        self.process(["int", "char", "boolean"])
        self.process([], True)
        while self.tokenizer.current_token == ",":
            self.process([","])
            self.process([], True)
        self.process([";"])
        self.output_stream.write("</varDec>\n")





    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        self.output_stream.write("<statements>\n")
        if self.tokenizer.current_token == "let":
            self.compile_let()
        elif self.tokenizer.current_token == "if":
            self.compile_if()
        elif self.tokenizer.current_token == "while":
            self.compile_while()
        elif self.tokenizer.current_token == "do":
            self.compile_do()
        elif self.tokenizer.current_token == "return":
            self.compile_return()
        self.output_stream.write("</statements>\n")




    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.output_stream.write("<doStatement>\n")
        self.process(["do"])
        self.compile_subroutine()
        self.output_stream.write("</doStatement>\n")



    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.output_stream.write("<letStatement>\n")
        self.process([], True)
        if self.tokenizer.current_token == "[":
            self.process(["["])
            # self.compile_expression()
            self.process(["]"])
        self.process(["="])
        # self.compile_expression()
        self.process([";"])
        self.output_stream.write("</letStatement>\n")







    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        self.output_stream.write("<whileStatement>\n")
        self.process(["while"])
        self.process(["("])
        # self.compile_expression()
        self.process([")"])
        self.process(["{"])
        self.compile_statements()
        self.process(["}"])
        self.output_stream.write("</whileStatement>\n")



    def write_token(self):
        if self.tokenizer.token_type() == "KEYWORD":
            self.output_stream.write\
                (f"<{self.lexical_elements_dict[self.tokenizer.token_type()]}>"
                 f" {self.tokenizer.current_token}"
                 f" </{self.lexical_elements_dict[self.tokenizer.token_type()]}>\n")
        elif self.tokenizer.token_type() == "SYMBOL":
            self.output_stream.write\
                (f"<{self.lexical_elements_dict[self.tokenizer.token_type()]}>"
                 f" {self.tokenizer.symbol()}"
                 f" </{self.lexical_elements_dict[self.tokenizer.token_type()]}>\n")



    def process(self, strings, is_identifier=False):
        if self.tokenizer.current_token in strings or is_identifier:
            self.write_token()
        else:
            raise SyntaxError
        self.tokenizer.advance()


    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        self.output_stream.write("<returnStatement>\n")
        self.process(["return"])
        if self.tokenizer.current_token != ";":
            # self.compile_expression()
            pass
        self.process([";"])
        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        self.output_stream.write("<ifStatement>\n")
        self.process(["if"])
        self.process(["("])
        # self.compile_expression()
        self.process([")"])
        self.process(["{"])
        self.compile_statements()
        self.process(["}"])
        if self.tokenizer.current_token == "else":
            self.process(["{"])
            self.compile_statements()
            self.process(["}"])
        self.output_stream.write("</ifStatement>\n")

    def compile_expression(self) -> None: #expression
        """Compiles an expression."""
        # Your code goes here!
        pass

    def compile_term(self) -> None: #expression
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None: #expression
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass
