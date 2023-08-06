
from descr.format import *
# from descr.terminal import *
from descr.html import *

pr = boxy_terminus()

# pr = boxy_terminus(rules = [
#         (".quack", {"background-color": "red"}),
#         (".{@False}", {":rearrange": lambda c, parts: ["F"],
#                        ":+classes": {}})])

dico = {"things": [True, False, None, 'yes!!!']}
v = [1, 2, 3, 4]
v = {(0, 1): (2, 3, 4, 5)}

# pr = std_terminal(
#     descr = augment_with_idclass(descr),
#     rules = [("top", {":after": "\n"}),
#              ("@False", {"color": 31}),
#              ("#"+str(id(dico)), {":+classes": "hl1"})
#              ]
#     )

pr([1, 2, 3, dico, "ordinary"])


# pr(v)

pr(["", '""', 1, 2, 3, [], {}, set()])

pr("what")
pr("what")
pr("what")
pr([1, 2, 3, [4, 5, 6], (7, 8, 9)])





# from descr import boxy_terminus, descr
# from descr.html.boxy import html_boxy
# from descr.html import HTMLRuleBuilder
# pr = boxy_terminus(rules = HTMLRuleBuilder().prop(".{@str}", ":+classes", lambda s: {"blue"} if s.endswith("Error") else {}).css_color(".{special}", "blue"))
# pr(["hello", 1, 2, 3, [4, 5, 6], True, False, None, dict(a = 1, b = 2, c = 3)])
# pr(dir(__builtins__))










# import sys
# import ast

# s = sys.argv[1]
# # s = """
# # def fact(n):
# #     if n <= 1:
# #         return 1
# #     else:
# #         return n * fact(n - 1)
# # """
# # s = """
# # try:
# #     x = d[k]
# # except Exception as e:
# #     print("damnit!")
# # else:
# #     print(x)
# # """

# pr(ast.parse(s))








txt = """
def fact(n):
    if n <= 1:
        return 1
    else:
    return n * fact(n - 1)

def fact(n):
    if n <= 1:
        return 1
    else:
        return n * fact(n - 1)

def fact(n):
    if n <= 1:
        return 1
    else:
        return n * fact(n - 1)
"""

# v = [(3, 9, {"hl3"}),
#      (2, 29, {"hl2"}),
#      (52, 52, {"hl1"}),]

# pr.write([{"pydescr"}, [{"pre"}] + highlight_lines(txt.split("\n"), v)])


# # v = [(1, 2),
# #      (5, 100),
# #      (10, 20),
# #      (11, 19),
# #      (15, 40)]

# # pr(morsel([x+(str(i),) for i, x in enumerate(v)]))

# # pr(["hello", "   hello", "hello world", "hello           world"])

import sys
import traceback, inspect, types
from descr import registry
from descr.highlight import *


pr0 = pr
pr = boxy_terminus(always_setup = False,
                   rules = RuleBuilder(

        (".path", {":rearrange": lambda x, y: [y[0].split("/")[-1]]}),
        (".source_loc", {"display": "none"}),
        (".source_header > *", {"margin": "0px", "padding": "0px"}),
        (".source_header > *", {"margin-right": "10px"}),
        (".traceback_separator", {"border": "0px"}),
        (".source_header", {"width": "350px"}),
        (".source_excerpt", {":+classes": "hstack"}),
        # (".lineno", {":+classes": "W#3"}),

        (".{@list} .{@list}", {"border": "4px solid #f00"}),
        (".{@list} .{@list} .{@list}", {"border": "4px solid #0f0"}),
        (".{@list} .{@list} .{@list} .{@list}", {"border": "4px solid #00f"}),
        (".{@tuple}", {"background-color": "#000"}),
        (".location", {":+classes": "C#2"}),
        # (".{+fname}", {"display": "none"}),
                   ))

# def f():
#     # from descr import wrong
#     # wrong.ugh()
#     open("nonExistant file",'r')

# try:
#     # f()
#     pr0.write(object())
# except:
#     try:
#         1/0
#     except:
#         (exc_type, exc_value, exc_traceback) = sys.exc_info()
#         # traceback.print_exception(exc_type, exc_value, exc_traceback)

#         # print("aaaa")
#         # print(exc_value, exc_value.__context__.__traceback__)
#         # print("aaaa")
#         # tb_list = traceback.extract_stack(exc_traceback)

#         # pr(dir(sys.exc_info()[2]))
#         # pr(sys.exc_info()[2])
#         # pr("====")

#         pr(exc_value)
#         pr(TypeError("This failed miserably :(", 2, 3, 4))

