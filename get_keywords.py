# -*- encoding:utf8 -*-
import codecs
import difflib
import json
import xlrd
from jieba.analyse import textrank, extract_tags
import jieba
from xlwt import Workbook

from strip_tags import strip_tags

def list2dict(listObj, num):
    dictObj = {}
    for ele in listObj:
        w_v = {}
        for w in list(dictObj.keys()):
            value = difflib.SequenceMatcher(None, ele[0], w).quick_ratio()
            if value > 0:
                print(w, ele[0], value)
            if value>0.6:
                w_v[w] = value
        if len(w_v)==0:
            dictObj[ele[0]] = ele[1]
        else:
            w_v_pair = sorted(dictObj.items(), key=lambda d: d[1], reverse=True)
            dictObj[w_v_pair[0][0]] += ele[1]
    for k in dictObj.keys():
        v = dictObj[k]
        v = v / num
        dictObj[k] = v
    dictObj = sorted(dictObj.items(), key=lambda d: d[1], reverse=True)
    return dictObj

def get_event_newslist_for_day():
    newsId = []
    newsType = []
    type2id = {}
    import xlrd
    data = xlrd.open_workbook('cluster_result_for_day/%d.xls' % day)
    table = data.sheets()[0]
    nrows = table.nrows
    for i in range(nrows):
        newsId.append(int(table.cell(i, 0).value))
        newsType.append(int(table.cell(i, 1).value))
    for i in range(len(newsType)):
        if newsType[i] in type2id:
            type2id[newsType[i]].append(newsId[i])
        else:
            type2id[newsType[i]] = [newsId[i]]
    newsType_set = []
    for ele in newsType:
        if ele not in newsType_set:
            newsType_set.append(ele)
    num_of_every_type = []
    for type in newsType_set:
        num = 0
        for ele in newsType:
            if ele == type:
                num += 1
        num_of_every_type.append(num)
    return newsId, newsType, newsType_set, num_of_every_type

def get_text_for_day():
    news_corpus = []
    for ele in newsId:
        f = codecs.open('../news_data/%d.json' % ele, encoding='utf-8')
        f_dict = json.load(f)
        title = f_dict["title"].replace("\r", "").replace("\n", "").replace("\r\n", "")
        if "，" not in title:
            title = title.replace(" ", "，")
        content = strip_tags(f_dict["content"].replace("\r", "").replace("\n", "").replace("\r\n", ""))
        news = title + "。" + content
        news_corpus.append(news)
    fout = open('event_text_for_day/%d_news.txt' % day, 'w', encoding='utf-8')
    for ele in news_corpus:
        fout.write(ele)
        fout.write('\n')
    fout.close()
    cluster_news_corpus = []
    for t in newsType_set:
        doc = ""
        for i in range(len(newsType)):
            if newsType[i] == t:
                doc = doc + news_corpus[i]
        cluster_news_corpus.append(doc)
    fout = open('event_text_for_day/%d.txt' % day, 'w', encoding='utf-8')
    for ele in cluster_news_corpus:
        fout.write(ele)
        fout.write('\n')
    fout.close()
    return news_corpus

def get_title_for_day():
    news_corpus = []
    for ele in newsId:
        f = codecs.open('../news_data/%d.json' % ele, encoding='utf-8')
        f_dict = json.load(f)
        title = f_dict["title"].replace("\r", "").replace("\n", "").replace("\r\n", "")
        if "，" not in title:
            title = title.replace(" ", "，")
        news_corpus.append(title)
    fout = open('event_text_for_day/%d_title.txt' % day, 'w', encoding='utf-8')
    for ele in news_corpus:
        fout.write(ele)
        fout.write('\n')
    fout.close()
    return news_corpus

def textrank_keywords(corpus):
    jieba.load_userdict('WordsDic/userdict_.txt')
    jieba.analyse.set_stop_words('WordsDic/stopwords.txt')
    k_n = []
    k_v = []
    for ele in corpus:
        news_n = textrank(ele, withWeight=True, allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'nrt', 'j'))
        news_v = textrank(ele, withWeight=True, allowPOS=('v', 'vn'))
        k_n.append(news_n)
        k_v.append(news_v)
    return k_n, k_v

def tfidf_keywords(corpus):
    jieba.load_userdict('WordsDic/userdict_.txt')
    jieba.analyse.set_stop_words('WordsDic/stopwords.txt')
    k_n = []
    k_v = []
    for ele in corpus:
        news_n = extract_tags(ele, withWeight=True, allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'nrt', 'j'))
        news_v = extract_tags(ele, withWeight=True, allowPOS=('v', 'vn'))
        k_n.append(news_n)
        k_v.append(news_v)
    return k_n, k_v

def main(corpus, f, type):
    if type == "content":
        keywords_noun, keywords_verb = textrank_keywords(corpus)
    if type == "title":
        keywords_noun, keywords_verb = tfidf_keywords(corpus)
    cluster_keywords_noun = []
    cluster_keywords_verb = []
    for t in newsType_set:
        kn = []
        kv = []
        for i in range(len(newsType)):
            if newsType[i] == t:
                kn.extend(keywords_noun[i])
                kv.extend(keywords_verb[i])
        cluster_keywords_noun.append(kn)
        cluster_keywords_verb.append(kv)
    fout = open(f, 'w', encoding='utf-8')
    for i in range(len(newsType_set)):
        linedict = {}
        num_of_news = num_of_every_type[i]
        k_n = cluster_keywords_noun[i]
        k_n_sort = list2dict(k_n, num_of_news)
        # print(type, k_n_sort)
        k_n_sort_ = [ele for ele in k_n_sort]
        linedict["noun"] = k_n_sort_
        k_v = cluster_keywords_verb[i]
        k_v_sort = list2dict(k_v, num_of_news)
        # print(type, k_v_sort)
        k_v_sort_ = [ele for ele in k_v_sort]
        linedict["verb"] = k_v_sort_
        strObj = json.dumps(linedict)
        fout.write(strObj)
        fout.write('\n')
    fout.close()

def get_cluster_title():
    cluster_title_corpus = []
    for t in newsType_set:
        cluster_title = ""
        for i in range(len(newsType)):
            if newsType[i] == t:
                cluster_title+=title[i]+"。"
        cluster_title_corpus.append(cluster_title)
    return cluster_title_corpus

def get_cluster_title_():
    cluster_title_corpus = []
    for t in newsType_set:
        cluster_title = []
        for i in range(len(newsType)):
            if newsType[i] == t:
                cluster_title.append(title[i])
        cluster_title_corpus.append(cluster_title)
    return cluster_title_corpus

def postprocess(f_t, f1, f2, cluster_title):
    f_t = open(f_t, 'r', encoding='utf-8')
    cluster_keywords_noun_title = []
    cluster_keywords_verb_title = []
    for line in f_t.readlines():
        line = eval(line)
        cluster_keywords_noun_title.append(line["noun"])
        cluster_keywords_verb_title.append(line["verb"])
    f_t.close()

    f = open(f1, 'r', encoding='utf-8')
    cluster_keywords_noun = []
    cluster_keywords_verb = []
    for line in f.readlines():
        line = eval(line)
        cluster_keywords_noun.append(line["noun"])
        cluster_keywords_verb.append(line["verb"])
    f.close()

    cluster_keywords_noun_post = []
    cluster_keywords_verb_post = []
    for i in range(len(newsType_set)):
        titles = cluster_title[i]
        noun = cluster_keywords_noun[i]
        print("content noun", noun)
        noun_title = cluster_keywords_noun_title[i]
        print("title noun", noun_title)
        noun_dict = {}
        for n in noun:
            num = 0
            for title in titles:
                if n[0] in title:
                    num += 1
            noun_dict[n[0]] = num/num_of_every_type[i]
        noun_dict = sorted(noun_dict.items(), key=lambda d: d[1], reverse=True)
        noun_post_ = [ele for ele in noun_dict if ele[1] > 0]
        print(noun_post_)
        if len(noun_post_) == 0:
            noun_post_ = noun_title
        print(noun_post_)
        noun_sum = sum([ele[1] for ele in noun_post_])
        noun_post = []
        for ele in noun_post_:
            word = ele[0]
            value = ele[1]
            value = value/noun_sum
            noun_post.append((word, value))
        print(noun_post)

        verb = cluster_keywords_verb[i]
        print("content verb", verb)
        verb_title = cluster_keywords_verb_title[i]
        print("title verb", verb_title)
        verb_dict = {}
        for v in verb:
            num = 0
            for title in titles:
                if v[0] in title:
                    num += 1
            verb_dict[v[0]] = num/num_of_every_type[i]
        max_value = max(list(verb_dict.values()))
        if len(verb_title) > 0:
            verb_dict[verb_title[0][0]] = max_value
        verb_dict = sorted(verb_dict.items(), key=lambda d: d[1], reverse=True)
        verb_post_ = [ele for ele in verb_dict if ele[1] > 0]
        print(verb_post_)
        if len(verb_post_) == 0:
            verb_post_ = verb_title
        print(verb_post_)
        verb_sum = sum([ele[1] for ele in verb_post_])
        verb_post = []
        for ele in verb_post_:
            word = ele[0]
            value = ele[1]
            value = value / verb_sum
            verb_post.append((word, value))
        print(verb_post)
        print("************************")


        cluster_keywords_noun_post.append(noun_post)
        cluster_keywords_verb_post.append(verb_post)
    fout = open(f2, 'w', encoding='utf-8')
    for i in range(len(newsType_set)):
        line_dict = {}
        line_dict["noun"] = cluster_keywords_noun_post[i]
        line_dict["verb"] = cluster_keywords_verb_post[i]
        strObj = json.dumps(line_dict)
        fout.write(strObj)
        fout.write('\n')
    fout.close()

def filter_cluster1(f_t, Id, Type, Type_set):
    t_v = []
    t_v_n = []
    f = open(f_t, 'r', encoding='utf-8')
    for line in f.readlines():
        line_dict = eval(line)
        t_v_n.append(line_dict)
        t_v.append(line_dict["verb"])
    f.close()
    # print(Id)
    # print(Type)
    t_v_zero = []
    for i in range(len(t_v)):
        if len(t_v[i])==0:
            t_v_zero.append(Type_set[i])

    # ------------------------------------------------
    f = open(f_t, 'w', encoding='utf-8')
    for ele in t_v_n:
        if len(ele['verb']) != 0:
            strObj = json.dumps(ele)
            f.write(strObj)
            f.write('\n')
    f.close()
    # ------------------------------------------------

    index_list = []
    for i in range(len(Type)):
        if Type[i] in t_v_zero:
            index_list.append(i)
    print(index_list)
    Id_ = [Id[i] for i in range(len(Id)) if i not in index_list]
    Type_ = [Type[i] for i in range(len(Type)) if i not in index_list]
    # print(Id_)
    # print(Type_)
    Type_set_ = []
    for ele in Type_:
        if ele not in Type_set_:
            Type_set_.append(ele)
    num_of_every_type = []
    for type in Type_set_:
        num = 0
        for ele in Type_:
            if ele == type:
                num += 1
        num_of_every_type.append(num)

    # ----------------------------------------------------------------------------------------
    title_corpus = []
    for ele in Id_:
        f = codecs.open('../news_data/%d.json' % ele, encoding='utf-8')
        f_dict = json.load(f)
        title = f_dict["title"].replace("\r", "").replace("\n", "").replace("\r\n", "")
        if "，" not in title:
            title = title.replace(" ", "，")
        title_corpus.append(title)

    book = Workbook()
    sheet1 = book.add_sheet('sheet1')
    for i in range(len(Id_)):
        row = sheet1.row(i)
        row.write(0, Id_[i])
        row.write(1, Type_[i])
        row.write(2, title_corpus[i])
    book.save('cluster_result_for_day/%d_.xls' % day)
    # ----------------------------------------------------------------------------------------

    return Id_, Type_, Type_set_, num_of_every_type


if __name__ == '__main__':
    num_of_days = 1
    for i in range(num_of_days):
        day = i + 1
        newsId, newsType, newsType_set, num_of_every_type = get_event_newslist_for_day()
        title = get_title_for_day()
        f_title = "textrank/%d_title.txt" % day
        main(title, f_title, "title")

        newsId, newsType, newsType_set, num_of_every_type = filter_cluster1(f_title, newsId, newsType, newsType_set)

        news = get_text_for_day()
        f_news = "textrank/%d_news.txt" % day
        f_news_post = "textrank/%d_news_post.txt" % day
        main(news, f_news, "content")

        title = get_title_for_day()
        cluster_title = get_cluster_title_()
        postprocess(f_title, f_news, f_news_post, cluster_title)

        # f = open('textrank/%d_news_post.txt' % day, 'r', encoding='utf-8')
        # keywords_list = []
        # for line in f.readlines():
        #     line_dict = eval(line)
        #     keywords_list.append(line_dict)
        # for i in range(len(newsType_set)):
        #     for j in range(num_of_every_type[i]):
        #         print(keywords_list[i]['noun'])
        # print("**************************************************")
        # for i in range(len(newsType_set)):
        #     for j in range(num_of_every_type[i]):
        #         print(keywords_list[i]['verb'])










