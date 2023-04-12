class Dialect:
    def __init__(
            self,
            delimiter:str='|',
            level_start:str='>',
            level_end:str='<',
            array_start:str='[',
            array_end:str=']',
            array_separator:str='^',
            line_break:str='\n'):
        self.delimiter = delimiter
        self.level_start = level_start
        self.level_end = level_end
        self.array_start = array_start
        self.array_end = array_end
        self.array_separator = array_separator
        self.line_break = line_break
        
default_dialect = Dialect()