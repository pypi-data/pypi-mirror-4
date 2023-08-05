class Colors(object):
    BOLD = 1
    DARK = 2
    UNDERLINE = 4
    BLINK = 5
    REVERSE = 7
    CONCEALED = 8
    ###
    GREY = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    ###
    BG_GREY = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47

    @staticmethod
    def c(text, *attributes):
        for attribute in attributes:
            text = '\033[%dm' % attribute + text
        return text + '\033[0m'


color = Colors.c
