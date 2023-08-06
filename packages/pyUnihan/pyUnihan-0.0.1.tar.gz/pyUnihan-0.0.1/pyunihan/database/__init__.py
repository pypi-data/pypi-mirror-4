import sys
py = sys.version_info
py3k = py >= (3, 0, 0)

if py3k:
    from database.database import uni_list
else:
    from database import uni_list