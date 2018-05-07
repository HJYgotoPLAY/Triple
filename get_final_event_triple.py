# -*- encoding:utf8 -*-
import difflib
def get_keywords():
    keyPredicate = []
    keyEntity = []
    f = open('textrank/%d_news_post.txt' % day)
    for line in f.readlines():
        line = eval(line)
        v = line['verb']
        if len(v) > 0:
            keyPredicate.append(v)
        else:
            keyPredicate.append([])
        n = line['noun']
        if len(n) > 0:
            keyEntity.append(n)
        else:
            keyEntity.append([])
    f.close()
    return keyPredicate, keyEntity

def get_event_newslist_for_day():
    newsType = []
    newsId = []
    import xlrd
    data = xlrd.open_workbook('cluster_result_for_day/%d_.xls' % day)
    table = data.sheets()[0]
    nrows = table.nrows
    for i in range(nrows):
        newsId.append(int(table.cell(i, 0).value))
        newsType.append(int(table.cell(i, 1).value))
    num_of_every_type = []
    newsType_set = []
    for ele in newsType:
        if ele not in newsType_set:
            newsType_set.append(ele)
    for type in newsType_set:
        num = 0
        for ele in newsType:
            if ele == type:
                num += 1
        num_of_every_type.append(num)
    return newsId, newsType, newsType_set, num_of_every_type

def get_event_triples():
    all_triples = []
    f = open('event_triples_for_day/%d_srl.txt' % day, 'r', encoding='utf-8')
    for line in f.readlines():
        if line != '\n':
            line = eval(line)
        all_triples.append(line)
    index = []
    for i in range(len(all_triples)):
        if all_triples[i] == '\n':
            index.append(i)
    event_triples_lists_ = []
    length = len(index)
    for i in range(len(index)):
        if i == 0:
            event_triples_lists_.append(all_triples[0: (index[i])])
        else:
            if (index[i] - index[i - 1]) > 2:
                event_triples_lists_.append(all_triples[(index[i - 1] + 1): (index[i])])
            else:
                event_triples_lists_.append(all_triples[index[i] - 1])
    event_triples_lists = []
    for ele in event_triples_lists_:
        if not isinstance(ele[0], list):
            event_triples_lists.append([ele])
        else:
            event_triples_lists.append(ele)
    event_triples_lists1 = []
    for i in range(len(event_triples_lists)):
        keywords_verb = keyPredicate[i]
        keywords_verb_word = [ele[0] for ele in keywords_verb]
        triples = event_triples_lists[i]
        triples_ = []
        for triple in triples:
            if triple[1] in keywords_verb_word:
                triples_.append(triple)
        if len(triples_) == 0:
            triples_ = event_triples_lists[i]
        event_triples_lists1.append(triples_)
    return event_triples_lists1

def get_final_triple():
    final_triples = []
    for i in range(len(event_triples_lists)):
        keywords_verb = keyPredicate[i]
        keywords_verb_word = [ele[0] for ele in keywords_verb]
        keywords_noun = keyEntity[i]
        keywords_noun_word = [ele[0] for ele in keywords_noun]
        print(keywords_verb)
        print(keywords_noun)
        event_triples = event_triples_lists[i]
        num_of_triples = len(event_triples)
        print([ele[1] for ele in event_triples])
        P_list = [ele[1] for ele in event_triples if ele[1] not in stopwords]
        P_set = set(P_list)
        P_dict_ = list2dict_v(P_list)
        P_dict_pair = sorted(P_dict_.items(), key=lambda d: d[1], reverse=True)
        print(P_dict_pair)
        P_dict = {}
        if len(P_dict_) > 1 and P_dict_pair[0][1] > P_dict_pair[1][1] * 3:
            P_dict[P_dict_pair[0][0]] = P_dict_pair[0][1]
        else:
            P_dict = P_dict_
        print(P_dict)

        if len(P_dict) >=2:
            P_dict_pair = sorted(P_dict.items(), key=lambda d: d[1], reverse=True)[:2]
        else:
            P_dict_pair = sorted(P_dict.items(), key=lambda d: d[1], reverse=True)
        print(P_dict_pair)
        triples_with_probability = {}
        for predicate in [ele[0] for ele in P_dict_pair]:
            p_predicate = P_dict_[predicate] / sum(list(P_dict_.values()))  # P(P)
            triple_with_predicate = []
            for triple in event_triples:
                if predicate in triple:
                    triple_with_predicate.append(triple)
            num = len(triple_with_predicate)
            A0_dict = list2dict([ele[0] for ele in triple_with_predicate])
            A1_dict = list2dict([ele[2] for ele in triple_with_predicate])
            sum_of_A0 = sum(list(A0_dict.values()))
            for ele in A0_dict.keys():
                p = A0_dict[ele] / sum_of_A0
                A0_dict[ele] = p
            sum_of_A1 = sum(list(A1_dict.values()))
            for ele in A1_dict.keys():
                p = A1_dict[ele] / sum_of_A1
                A1_dict[ele] = p
            print(A0_dict)
            print(A1_dict)
            if predicate in keywords_verb_word:
                index_v = keywords_verb_word.index(predicate)
                p_v = keywords_verb[index_v][1]
            else:
                keywords_verb_value = [ele[1] for ele in keywords_verb]
                min_value = min(keywords_verb_value)
                p_v = min_value
            print("&&", predicate, p_predicate, p_v)
            for a0 in A0_dict.keys():
                for a1 in A1_dict.keys():
                    if a0!='' and predicate in a0:
                        p = 0
                    elif a1!='' and predicate in a1:
                        p = 0
                    else:
                        pa0 = A0_dict[a0]
                        pa1 = A1_dict[a1]
                        # print(a0, pa0, a1, pa1)
                        score_list_a0 = []
                        for ele in keywords_noun_word:
                            score = difflib.SequenceMatcher(None, ele, a0).quick_ratio()
                            score_list_a0.append(score)
                        max_a0 = max(score_list_a0)
                        index_a0 = score_list_a0.index(max_a0)
                        min_a0 = min([ele[1] for ele in keywords_noun])
                        if max_a0>0.4:
                            pa0*=keywords_noun[index_a0][1]
                        else:
                            pa0*=(min_a0/2)
                        score_list_a1 = []
                        for ele in keywords_noun_word:
                            score = difflib.SequenceMatcher(None, ele, a1).quick_ratio()
                            score_list_a1.append(score)
                        max_a1 = max(score_list_a1)
                        index_a1 = score_list_a1.index(max_a1)
                        min_a1 = min([ele[1] for ele in keywords_noun])
                        if max_a1 > 0.4:
                            pa1 *= keywords_noun[index_a1][1]
                        else:
                            pa1 *= (min_a1/2)
                        # print(a0, pa0, a1, pa1)
                        p = pa0*p_v*p_predicate*pa1
                        # print("p", p)
                        if len(a0) == 0 or len(a1) == 0:
                            p=p/10
                        Obj = (a0, predicate, a1)

                    triples_with_probability[Obj] = p
        triples_with_probability_pair = sorted(triples_with_probability.items(), key=lambda d: d[1], reverse=True)[:10]
        for ele in triples_with_probability_pair:
            print(ele)
        if len(triples_with_probability_pair)>0:
            top_triple = list(triples_with_probability_pair[0][0])
            if top_triple[0] == top_triple[2] == '' and len(triples_with_probability_pair) > 1:
                top_triple = list(triples_with_probability_pair[1][0])
            if top_triple[0] == top_triple[2] and len(triples_with_probability_pair)>1:
                if triples_with_probability_pair[0][1]==triples_with_probability_pair[1][1]:
                    top_triple = list(triples_with_probability_pair[1][0])
                else:
                    top_triple = [top_triple[0], top_triple[1], '']
            if difflib.SequenceMatcher(None, top_triple[0], top_triple[2]).quick_ratio() >= 0.5 and len(triples_with_probability_pair)>1:
                if difflib.SequenceMatcher(None, list(triples_with_probability_pair[1][0])[0], list(triples_with_probability_pair[1][0])[2]).quick_ratio() < 0.5:
                    top_triple = list(triples_with_probability_pair[1][0])
            if top_triple[0] == '':
                if difflib.SequenceMatcher(None, top_triple[2], keywords_noun_word[0]).quick_ratio() == 0:
                    top_triple[0] = keywords_noun_word[0]
            if top_triple[2] == '':
                if difflib.SequenceMatcher(None, top_triple[0], keywords_noun_word[0]).quick_ratio() == 0:
                    top_triple[2] = keywords_noun_word[0]
        else:
            top_triple=[]
        final_triples.append(top_triple)
        print("top triple", top_triple)
        print('----------------------------------------------------------------------------------------------------------')
    return final_triples

def list2dict_v(listObj):
    dictObj = {}
    for ele in listObj:
        if ele in dictObj:
            dictObj[ele] += 1
        else:
            dictObj[ele] = 1
    return dictObj

def list2dict(listObj):
    stopwords = ['是', '的', '同比', '我', '我们', '你', '你们', '他', '他们']
    dictObj = {}
    if len(set(listObj)) == 1 and list(set(listObj))[0] == '':
        for ele in listObj:
            if ele in dictObj:
                dictObj[ele] += 1
            else:
                dictObj[ele] = 1
    else:
        for ele in listObj:
            if ele not in stopwords and len(ele) <= 20 and len(ele)>1:
                if ele in dictObj:
                    dictObj[ele] += 1
                else:
                    dictObj[ele] = 1
    key_list = list(dictObj.keys())
    value_list = list(dictObj.values())

    matrix = []
    for e1 in key_list:
        l = []
        for e2 in key_list:
            score = difflib.SequenceMatcher(None, e1, e2).quick_ratio()
            l.append(score)
        matrix.append(l)
    index = []
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] > 0.4:
                if i!=j:
                    index.append(i)
                    index.append(j)
    index_ = list(set(index))
    value_list_ = []
    for i in range(len(value_list)):
        v = 1
        if i in index_:
            v*=value_list[i]*len(index_)
        else:
            v*=value_list[i]
        value_list_.append(v)
    dictObj_ = {}
    for i in range(len(value_list)):
        dictObj_[key_list[i]] = value_list_[i]
    return dictObj_

if __name__ == '__main__':
    num_of_days = 1
    f_stopwords = open('WordsDic/stopwords.txt', 'r', encoding='utf-8')
    stopwords = []
    for line in f_stopwords.readlines():
        line = line.strip()
        stopwords.append(line)
    for i in range(num_of_days):
        day = i + 1
        keyPredicate, keyEntity = get_keywords()
        newsId, newsType, newsType_set, num_of_every_type = get_event_newslist_for_day()
        event_triples_lists = get_event_triples()
        final_triples = get_final_triple()

        f_triple = open('event_final_triples_for_day/%dsrl.txt' % day, 'w', encoding='utf-8')
        for t in final_triples:
            f_triple.write(str(t))
            f_triple.write('\n')
        f_triple.close()

        for i in range(len(final_triples)):
            for j in range(num_of_every_type[i]):
                print(final_triples[i])
        print('------------------------------------------------')
        for i in range(len(keyPredicate)):
            for j in range(num_of_every_type[i]):
                k_v = keyPredicate[i][:2]
                k_v_ = []
                for ele in k_v:
                    k_v_.append(ele[0])
                print(k_v_)
        print('------------------------------------------------')
        for i in range(len(keyEntity)):
            for j in range(num_of_every_type[i]):
                k_n = keyEntity[i][:2]
                k_n_ = []
                for ele in k_n:
                    k_n_.append(ele[0])
                print(k_n_)