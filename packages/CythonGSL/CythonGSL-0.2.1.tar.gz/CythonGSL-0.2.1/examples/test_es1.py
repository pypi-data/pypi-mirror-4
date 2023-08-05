import sys
mod1 = sys.argv[1]
mod1 = __import__(mod1)

getattr(mod1,"main")()
