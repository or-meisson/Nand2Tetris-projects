"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the lines end.

    - xxx: quotes are used for tokens that appear verbatim (terminals).
    - xxx: regular typeface is used for names of language constructs 
           (non-terminals).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """




    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input_lines = list(filter(
            lambda x: x and not x.startswith("//"),
            map(str.strip, input_stream.read().splitlines())))

        # self.input_lines = [
        #     line.split('//', 1)[0].rstrip() if not self.is_in_string else line for line
        #     in self.input_lines]
        # self.is_in_string = False
        self.input_lines = self.remove_multi_line_comments(self.input_lines)
        # self.input_lines = [line.split('//', 1)[0].rstrip() for line in
        #                     self.input_lines]
        self.input_lines = [line.replace('\t', ' ') for line in self.input_lines]
        # print(self.input_lines)
        self.current_line = ""
        self.current_line_idx = 0
        self.current_char_idx = 0
        self.current_char = ""
        self.current_token = ""
        self.keyword_list = ["class", "constructor", 'function', 'method',
                             'field',
                             'static', 'var', 'int', 'char', 'boolean', 'void',
                             'true',
                             'false', 'null', 'this', 'let', 'do', 'if',
                             'else',
                             'while', 'return']
        self.symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                            '-', '*', '/', '&', '|', '<', '>', '=', '~', '^',
                            '#']
        self.token_is_identifier = False
        self.token_is_string = False

    def has_more_tokens(self) -> bool:  # in all the input
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        if self.current_line_idx + 1 == len(
                self.input_lines) and self.current_char_idx == len(
            self.current_line):
            return False
        return True




    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.token_is_identifier = False
        self.token_is_string = False
        if not self.current_line:  # the very start
            self.current_line = self.input_lines[self.current_line_idx]
        if self.current_char_idx == len(self.current_line):  # last char in line
            self.current_line_idx += 1
            self.current_line = self.input_lines[self.current_line_idx]
            self.current_char_idx = 0
        self.current_char = self.current_line[self.current_char_idx]

        while self.current_char == " ":  # char is blank space
            self.current_char_idx += 1
            self.current_char = self.current_line[self.current_char_idx]
        if self.current_char in self.symbol_list:
            self.current_token = self.current_char
            self.current_char_idx += 1
            return
        elif self.current_char == '"':
            self.get_string_token()
        elif self.current_char.isdigit():
            self.get_integer_token()
            self.current_char_idx += 1
            return
        else:
            self.get_token_till_next_blank_space()
            return

    def get_string_token(self):
        token = ""
        self.current_char_idx += 1
        self.current_char = self.current_line[self.current_char_idx]
        while self.current_char != '"':
            token += self.current_char
            self.current_char_idx += 1
            self.current_char = self.current_line[self.current_char_idx]
        self.current_char_idx += 1
        self.current_token = token
        self.token_is_string = True

    def get_integer_token(self):
        integer_string = ""
        while self.current_char.isdigit():
            integer_string += self.current_char
            self.current_char_idx += 1
            self.current_char = self.current_line[self.current_char_idx]
        self.current_char_idx -= 1
        self.current_token = integer_string

    def get_token_till_next_blank_space(self):
        end_of_line = False
        token = ""
        while self.current_char != " " and self.current_char not in self.symbol_list:
            if self.current_char_idx == len(self.current_line):
                end_of_line = True
                token += self.current_char
                self.current_line_idx += 1
                self.current_line = self.input_lines[self.current_line_idx]
                self.current_char_idx = 0
                break
            self.current_char = self.current_line[self.current_char_idx]
            token += self.current_char

            self.current_char_idx += 1

        if token in self.keyword_list:
            self.current_token = token[:-1]
            if not end_of_line:
                self.current_char_idx -= 1
        else:
            self.token_is_identifier = True
            self.current_token = token[:-1]
            if not end_of_line:

                self.current_char_idx -= 1



    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.current_token in self.symbol_list:
            return "SYMBOL"
        elif self.current_token in self.keyword_list:
            return "KEYWORD"

        elif self.token_is_identifier:
            return "IDENTIFIER"
        elif self.token_is_string:
            return "STRING_CONST"
        elif self.current_token[0].isdigit():
            return "INT_CONST"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        return self.current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        if self.current_token == "<":
            return "&lt;"
        elif self.current_token == ">":
            return "&gt;"
        elif self.current_token == "&":
            return "&amp;"
        return self.current_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        # Your code goes here!
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        return self.current_token

    def remove_multi_line_comments(self, input_lines):
        preprocessed_lines = []
        # Flag to determine if currently inside a multi-line comment
        in_multiline_comment = False

        # Flag to determine if currently inside a string
        in_string = False

        # Iterate through each line
        for line in input_lines:
            processed_line = ""
            i = 0
            while i < len(line):
                if line[i] == '"':
                    # Toggle the in_string flag
                    in_string = not in_string
                # Check if the line contains a multi-line comment
                if line[i:i + 2] == "/*" and not in_string:
                    # Set the flag to True since we are inside a multi-line comment
                    in_multiline_comment = True
                    while i < len(line) and line[i:i + 2] != "*/":
                        i += 1
                    # Check if the multi-line comment ends on the same line
                    if i < len(line):
                        # Skip the multi-line comment
                        i += 2
                        # Set the flag to False since the multi-line comment has ended
                        in_multiline_comment = False
                        continue
                    else:
                        # Exit the loop if the multi-line comment continues onto the next line
                        break
                # Check if the multi-line comment ends on the same line
                if line[
                   i:i + 2] == "*/" and in_multiline_comment and not in_string:
                    i += 2
                    # Set the flag to False since the multi-line comment has ended
                    in_multiline_comment = False
                    continue
                if line[i:i + 2] == "//" and not in_string:
                    # If we encounter '//' and not inside a string, we stop processing the line
                    break
                if not in_multiline_comment:
                    processed_line += line[i]
                i += 1
            # Add the preprocessed line to the list
            preprocessed_lines.append(processed_line.strip())

        preprocessed_lines = list(
            filter(lambda x: x != '', preprocessed_lines))
        return preprocessed_lines

