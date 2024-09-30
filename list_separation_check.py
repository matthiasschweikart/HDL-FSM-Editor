"""
This class gets a string which contains a list, where the elements are separated with ';' (VHDL) or ',' (Verilog).
If the user did end the last element of the list also with this separator,
the class must remove the separator from the last element (as this is the only correct HDL syntax).
Removing of this separator is not so easy, as the separator might also be used in comments which are placed in the list.
For removing first a copy of the string is created where all block-comments are replaced by blanks.
Then all comments at the end of each line contained in the copied string are also replaced by blanks.
Last the characters in the copied string are analyzed starting at the end of the copied string:
If the first character which is different from blank or return is not the separator,
the search is ended and nothing done else, because the user did not insert an illegal separator.
But if the character is the separator its index is used to replace it by blank in the original string,
afterwards the search is ended.
"""
import re

class ListSeparationCheck():
    def __init__(self, list_string, language):
        self.list_string = list_string
        if language=="VHDL":
            separator          = ';'
            comment_identifier = "--"
        else:
            separator          = ','
            comment_identifier = "//"
        list_string_without_block_comment = self.__replace_block_comments_by_blank(list_string)
        list_string_without_comments      = self.__replace_all_comments_at_line_end(list_string_without_block_comment, comment_identifier)
        self.__remove_illegal_separator(list_string_without_comments, separator)

    def get_fixed_list(self):
        return self.list_string

    def __replace_block_comments_by_blank(self, list_string):
        while True:
            match_object = re.search(r"/\*.*?\*/", list_string, flags=re.DOTALL)
            if match_object is None:
                break
            list_string = list_string[:match_object.span()[0]] + ' '*(match_object.span()[1]-match_object.span()[0]) + list_string[match_object.span()[1]:]
        return list_string

    def __replace_all_comments_at_line_end(self, list_string_without_block_comment, comment_identifier):
        list_array = list_string_without_block_comment.split("\n")
        list_string_without_comments = ""
        for line in list_array:
            list_string_without_comments += self.__replace_comment_at_line_end_by_blank(comment_identifier, line) + "\n"
        return list_string_without_comments[:-1] # remove last return

    def __replace_comment_at_line_end_by_blank(self, comment_identifier, line):
        match_object = re.search(comment_identifier + ".*", line)
        if match_object is not None:
            line = line[:match_object.span()[0]] + ' '*(match_object.span()[1]-match_object.span()[0]) + line[match_object.span()[1]:]
        return line

    def __remove_illegal_separator(self, list_string_without_comments, separator):
        for index, char in enumerate(reversed(list_string_without_comments)):
            if char not in (' ', '\n'):
                if char==separator:
                    self.__remove_character_by_blank(index)
                break

    def __remove_character_by_blank(self, index):
        if index==0:
            self.list_string = self.list_string[:-index-1]
        else:
            self.list_string = self.list_string[:-index-1] + ' ' + self.list_string[-index:]
