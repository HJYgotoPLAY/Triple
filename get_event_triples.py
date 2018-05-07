# -*- encoding:utf8 -*-
import json
import codecs

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

def get_event_sentences():
    sentences_lists = []
    f = open('event_sentences_for_day/%d.txt' % day, 'r', encoding='utf-8')
    for line in f.readlines():
        line_dict = eval(line)
        sentences_lists.append(list(line_dict.values())[0])
    return sentences_lists

def get_event_triples_srl():
    words = segmentor.segment(sentence)  # 分词
    words = '\t'.join(words)
    words = words.split('\t')
    # print(words)
    postags = postagger.postag(words)  # 词性标注
    postags = '\t'.join(postags)
    postags = postags.split('\t')
    arcs = parser.parse(words, postags)  # 句法分析
    roles = labeller.label(words, postags, arcs)  # 语义角色标注
    triplesAll = []
    for role in roles:
        triples = ['', '', '']
        role = role.index, "".join(["%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end) for arg in role.arguments])
        predicate = words[role[0]]
        print(predicate)
        triples[1] = predicate
        args = role[1].split(")")
        args.remove('')
        for ele in args:
            ele = ele.split(":")
            if ele[0] == "A0":
                index = ele[1][1:].split(",")
                A0 = words[int(index[0]):int(index[1])+1]
                A0_str = "".join(A0)
                triples[0] = A0_str
            if ele[0] == "A1":
                index = ele[1][1:].split(",")
                A1 = words[int(index[0]):int(index[1]) + 1]
                A1_str = "".join(A1)
                triples[2] = A1_str
        print(triples)
        triplesAll.append(triples)
    return triplesAll

if __name__ == '__main__':
    num_of_days = 1
    for i in range(num_of_days):
        day = i + 1

        keyPredicates_lists = key_predicate()
        keyEntities_lists = key_entity()

        import os
        from pyltp import Segmentor, Postagger, Parser, SementicRoleLabeller
        LTP_DATA_DIR = 'ltp_data_v3.4.0'  # ltp模型目录的路径
        cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
        pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
        par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`
        srl_model_path = os.path.join(LTP_DATA_DIR, 'pisrl_win.model')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。
        segmentor = Segmentor()
        segmentor.load_with_lexicon(cws_model_path, 'WordsDic/userdict.txt')  # 加载模型，第二个参数是外部词典文件路径
        postagger = Postagger()
        postagger.load_with_lexicon(pos_model_path, 'WordDic/userdict_.txt')
        parser = Parser()
        parser.load(par_model_path)
        labeller = SementicRoleLabeller()
        labeller.load(srl_model_path)

        # ------------------------------------------------------------------------------
        # pyltp-srl
        sentences_lists = get_event_sentences()
        fout = open('event_triples_for_day/%d_srl.txt' % day, 'w', encoding='utf-8')
        for i in range(len(sentences_lists)):
            sentences = sentences_lists[i]
            keyPredicates = keyPredicates_lists[i]
            keyEntities = keyEntities_lists[i]
            for sentence in sentences:
                event_triple = get_event_triples_srl()
                for ele in event_triple:
                    fout.write(str(ele))
                    fout.write('\n')
            fout.write('\n')
        fout.close()
        # ------------------------------------------------------------------------------

        segmentor.release()
        postagger.release()
        parser.release()
        labeller.release()



