# -*- encoding:utf8 -*-
import json
import codecs
from pyltp import SentenceSplitter

def get_event_newsId_for_day():
    newsId = []
    newsType = []
    newsId_for_event = []
    import xlrd
    data = xlrd.open_workbook('cluster_result_for_day/%d_.xls' % day)
    table = data.sheets()[0]
    nrows = table.nrows
    for i in range(nrows):
        newsId.append(int(table.cell(i, 0).value))
        newsType.append(int(table.cell(i, 1).value))
    newsTypeSet = []
    for ele in newsType:
        if ele not in newsTypeSet:
            newsTypeSet.append(ele)
    type2id = {}
    for i in range(len(newsType)):
        if newsType[i] in type2id:
            type2id[newsType[i]].append(newsId[i])
        else:
            type2id[newsType[i]] = [newsId[i]]
    for ele in newsTypeSet:
        news = type2id[ele]
        newsId_for_event.append(news)
    return newsId_for_event

def key_predicate():
    keyPredicate = []
    f = open('textrank/%d_news_post.txt' % day)
    for line in f.readlines():
        line = eval(line)
        v = line['verb']
        if len(v) > 0:
            keyPredicate.append(v)
        else:
            keyPredicate.append('')
    return keyPredicate

def key_entity():
    keyEntity = []
    f = open('textrank/%d_news_post.txt' % day)
    for line in f.readlines():
        line = eval(line)
        e = line['noun']
        if len(e) > 0:
            keyEntity.append(e)
        else:
            keyEntity.append('')
    return keyEntity

def get_sentences_lists():
    event_text = []
    f = open('event_text_for_day/%d.txt' % day, 'r', encoding='utf-8')
    for line in f.readlines():
        event_text.append(line)
    Sentences_lists = []
    for ele in event_text:
        sents = SentenceSplitter.split(ele)
        sents = '\n'.join(sents)
        sents = sents.split('\n')
        # ---------------------------------------------------------------
        # 用pyltp分句后对于长句子的处理——如果为长句子（大于一定长度）则根据句子中的“，”继续将句子进行划分
        sents_ = []
        for sen in sents:
            if len(sen) > 10 and "，" in sen:
                sen = sen.split("，")
                for ele in sen:
                    sents_.append(ele)
            else:
                sents_.append(sen)
        k_s = []
        for ele in sents_:
            if len(ele) >= 5 and len(ele) <= 70:
                if '：' in ele:
                    index = ele.index('：')
                    ele = ele[index + 1:]
                elif '传' in ele:
                    index = ele.index('传')
                    ele = ele[index + 1:]
                elif '称' in ele:
                    index = ele.index('称')
                    ele = ele[index + 1:]
                elif '说' in ele:
                    index = ele.index('说')
                    ele = ele[index + 1:]
                k_s.append(ele)
                for ele in k_s:
                    print(ele)
        Sentences_lists.append(k_s)
        # ---------------------------------------------------------------
    return Sentences_lists

def get_key_sentences():
    line_dict = {}
    # print(keyPredicates, end='')
    # print(keyEntities)
    key_sentences = sentences
    line_dict[keyPredicates[0][0]] = key_sentences
    strObj = json.dumps(line_dict)
    fout.write(strObj)
    fout.write('\n')

if __name__ == '__main__':
    num_of_days = 1
    for i in range(num_of_days):
        day = i + 1
        newsId_for_event = get_event_newsId_for_day()
        keyPredicates_lists = key_predicate()
        keyEntities_lists = key_entity()
        sentences_lists = get_sentences_lists()
        fout = open('event_sentences_for_day/%d.txt' % day, 'w', encoding='utf-8')
        for i in range(len(sentences_lists)):
            news = newsId_for_event[i]
            keyPredicates = keyPredicates_lists[i]
            keyEntities = keyEntities_lists[i]
            sentences = sentences_lists[i]
            get_key_sentences()
        fout.close()






