import argparse
from pygtrans import Translate
from IPython import embed
from tqdm import tqdm
import os
import random
import codecs

def get_max_index():
    '''
    Description:
        获取当前所有单词本中最大编号max_index，则新生成的单词本编号为max_index+1
    Returns:
        max_index( int ):最大的单词本编号
    '''
    max_index = 0
    try:
        for _,_,files in os.walk('./wordbook'):
            for file in files:
                if(file.endswith('.txt')):
                    now_index = ''
                    # now_index代表file这个txt文件的数字编号，使用isdigit函数加上字符串拼接得到该数字
                    for i in file:
                        if(str.isdigit(i)):
                            now_index += i
                        else:
                            now_index += ''
                    max_index = max(max_index, int(now_index))
        return max_index
    except Exception as e:
        embed(header = str(e))


def parser_data():
    '''
    Description:
        本程序为参数解析器，用于读取命令行参数并完成相应功能，相关参数如下约定：
        1. -r/--random:在生词表中随机选取单词产生单词本，若不输入-r参数则默认为false，表示有序选取。
        2. -n/--num:选取的单词数目，若不输入-n参数则默认为40个。
        3. -s/--start:在生词表中选取的单词区间左端点编号，若不输入-s参数则默认为0
        4. --end:在生词表中选取的单词区间右端点编号，若不输入--end参数则默认为100。该参数与-s参数一同构成了生词的选取区间[start, end)。
        若用户要求随机选取单词，则先选取出原生词表中制指定的区间[start,end),再在其中随机选取num个生词。
    '''
    parser = argparse.ArgumentParser(
        prog = 'Word Translator',
        description = 'choose the length and the style of the translator',
        epilog = '不会写介绍，轻喷'
    )
    parser.add_argument(
        '-r',
        '--random',
        action='store_true',
        dest = 'random',
        default = False,
        help = '选择是否随机产生生词，若不输入-r则代表有序生成,输入-r代表随机生成'
    )
    parser.add_argument(
        '-n',
        '--num',
        dest = 'num',
        type = int,
        default = 40,
        help = '在生词表选取的单词数目'
    )
    parser.add_argument(
        '-s',
        '--start',
        dest = 'start',
        type = int,
        default = 0,
        help = '在生词表中选取的单词起点编号'
    )
    parser.add_argument(
        '--end',
        dest = 'end',
        type = int,
        default = 100,
        help = '用户希望选取的生词表区间长度'
    )
    args = parser.parse_args()
    return args.random,args.num,args.start,args.end

def Assemble(head_str, num, tail_str):
    '''
    Description:
        组装字符串与数字，从而得到读入输出文件的全名
    '''
    return head_str + str(num) + tail_str

def make_translate(rand, num, start, end, index):
    '''
    Description:
        根据传入参数进行翻译，并将翻译结果写入新生成的txt文件
    Args:
        rand( bool ): 是否随机生成单词本
        num( int ): 单词本中单词的数目
        start( int ): 在生词表中选取的单词区间左端点编号
        end( int ): 在生词表中选取的单词区间右端点编号（左开右闭）
        index( int ): 最大单词表的编号加1，即是新生成的单词表的编号
    '''
    try:
        translator = Translate(proxies={'https':'socks5://localhost:2801'},domain='com')
        # 2801为本地代理的端口
    except Exception as e:
        embed(header=str(e))
    file = codecs.open('./collection.txt', 'r')
    initial_words = list(filter(None, file.read().split('\n')))
    # 去除生词表中多余的换行符
    if( end >= len(initial_words) or start > end ):
        return "选取的生词区间不合法，翻译失败"
    else:
        initial_words = initial_words[start:end]
        if( num > ( end - start )):
            num = end - start
    try: 
        if rand:
            initial_words = random.sample(initial_words, num)
        else:
            initial_words = initial_words[0:num]
    except Exception as e:
        embed(header=str(e))
    file = codecs.open(Assemble('./wordbook/untraslated_', index, '.txt'),'w','utf-8')
    # 使用codecs，从而规定输出文件编码方式为utf-8
    for i in tqdm(range(num)):
        word = initial_words[i]
        file.write(Assemble('第', i + 1, '个词组:'))
        try:
            word = word.split(',')
            for each in word:
                each = each.strip()
                # 去除每一个字符前后的空格
                file.write(each+'  ')
            file.write('\n')
        except Exception as e:
            embed(header=str(e))
    file = codecs.open(Assemble('./wordbook/traslated_', index, '.txt'),'w','utf-8')
    for i in tqdm(range(num)):
        word = initial_words[i]
        file.write(Assemble('第', i + 1, '个词组:'))
        try:
            word = word.split(',')
            for each in word:
                each = each.strip()
                # 去除每一个字符前后的空格
                answer = each + ':' + translator.translate(each,target='zh-CN').translatedText + ' '
                file.write(answer)
            file.write('\n')
        except Exception as e:
            embed(header=str(e))
    return None

if __name__ == "__main__":
    make_translate(*parser_data(), get_max_index() + 1)