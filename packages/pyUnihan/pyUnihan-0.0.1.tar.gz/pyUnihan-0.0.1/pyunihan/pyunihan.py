# -*- coding: utf-8 -*-

import sys
import database

py = sys.version_info
py3k = py >= (3, 0, 0)

uni_list = []
radicial_list = ('一一丨丶丿乙亅二亠人儿入八冂冖冫几'
    '凵刀力勹匕匚匸十卜卩厂厶又口囗土士夂夊夕大女子宀寸小'
    '尢尸屮山巛工己巾干幺广廴廾弋弓彐彡彳心戈戶手支攴文斗'
    '斤方无日曰月木欠止歹殳毋比毛氏气水火爪父爻爿片牙牛犬'
    '玄玉瓜瓦甘生用田疋疒癶白皮皿目矛矢石示禸禾穴立竹米糸'
    '缶网羊羽老而耒耳聿肉臣自至臼舌舛舟艮色艸虍虫血行衣襾'
    '見角言谷豆豕豸貝赤走足身車辛辰辵邑酉釆里金長門阜隶隹'
    '雨靑非面革韋韭音頁風飛食首香馬骨高髟鬥鬯鬲鬼魚鳥鹵鹿'
    '麥麻黃黍黑黹黽鼎鼓鼠鼻齊齒龍龜龠')

if py3k:
    r8dicial_list = list(radicial_list)
else:
    radicial_list = list(radicial_list.decode('utf-8'))

def init():
    global uni_list
    uni_list = database.uni_list

def init_old():
    global uni_list
    fi = open("database", "r").readlines()
    uni_list = {}
    
    for i in fi:
        i = i.strip("\n").split(" ")
        uni_list[int(i[0][2:], 16)] = [
            radicial_list[int(i[2][:i[2].find(".")].replace("'", ""))], i[1], i[2]]
    
    open("database.py", "w").write("uni_list=%s" % repr(uni_list))
 
def get_radical(char):
    """Return chinese charater redical, TotalStrokes, RSUnicode
    *RSUnicode: Radical-Stroke Counts
    
    >>> init()
    >>> get_radical("我")
    ['戈', '7', '62.3']
    """
    if py3k:
        if not isinstance(char, str):
            char = char.decode('utf-8')
    else:
        if not isinstance(char, unicode):
            char = char.decode('utf-8')
        
    char = ord(char)
    return uni_list[char]
    
if __name__ == '__main__':
    import time
    t = time.time()
    print(get_radical("我"))
    print(get_radical("豺"))
    print(time.time() - t)