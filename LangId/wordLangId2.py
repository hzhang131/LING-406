import codecs
import re
import bisect
import math
import copy
import bisect

def driver(filename_lst, filename, sol):
    """
    driver code for the word-bigram language identification code using Good Turing Algorithm.
    """
    all_prob_en = {}
    all_prob_fr = {}
    all_prob_it = {}
    single_token_dict_en = {}
    single_token_dict_fr = {}
    single_token_dict_it = {}
    prob_list = wordLangId(filename_lst, all_prob_en, all_prob_fr, all_prob_it, single_token_dict_en, single_token_dict_fr, single_token_dict_it)
    lst = LangId("LangId.test", prob_list[0], prob_list[1], prob_list[2], single_token_dict_en, single_token_dict_fr, single_token_dict_it)
    out_str = ""
    for i in lst:
        out_str += i
        out_str += "\n"
    codecs.open("wordLangId2.out", "w").write(out_str)
    sol_ = codecs.open(sol, "r").read()
    count = 0
    errorCount = 0
    errorList = []
    res_list = re.findall(r'\s(:?English|French|Italian)\s', sol_)
    for i in range(0, len(res_list)):
        count += 1
        if res_list[i] != lst[i]:
            errorCount += 1
            errorList.append(count - 1)
    print("Accuracy of word-bigram model with GT is: ", (count - errorCount)/count * 100.0, "%.")
    print("Output saved to wordLangId2.out")
    # print("Total: ", count)
    # print("Missed: ", errorCount)
    # print("Zero-based indices are: ", errorList)
    return

def wordLangId(filename_lst, all_prob_en, all_prob_fr, all_prob_it, single_token_dict_en, single_token_dict_fr, single_token_dict_it):
    output_str = ""
    for file in filename_lst:
        lst = re.findall(r'(?:English|French|Italian)', file, re.IGNORECASE)
        lang_tag = ""
        if lst[0] == "English":
           lang_tag = "en"
        elif lst[0] == "French":
            lang_tag = "fr"
        elif lst[0] == "Italian":
            lang_tag = "it"
        # calculate probs of word bigrams. includes apostrophes but ignores comma and period.
        s = codecs.open(file, 'r', 'iso-8859-1').read()
        sentence_list = re.findall(r'(?:.*)\s', s)
        for i in sentence_list:
            output_str += i
            output_str += "\n"
        if lang_tag == "en":
            all_prob_en = wordprob(sentence_list, lang_tag, s, single_token_dict_en)
        if lang_tag == "fr":
            all_prob_fr = wordprob(sentence_list, lang_tag, s, single_token_dict_fr)
        if lang_tag == "it":
            all_prob_it = wordprob(sentence_list, lang_tag, s, single_token_dict_it)
    return [all_prob_en, all_prob_fr, all_prob_it]

def wordprob(lst, lang_tag, s, single_token_dict):
        vocab_lst = s.split(' ')
        while '\n' in vocab_lst:
            vocab_lst.remove('\n')
        while '.' in vocab_lst:
            vocab_lst.remove('.')
        while ',' in vocab_lst:
            vocab_lst.remove(',')
        while '.\n' in vocab_lst:
            vocab_lst.remove('.\n')
        
        local_dict = {}
        all = {}

        for i in vocab_lst:
            if i in local_dict:
                single_token_dict[i] += 1
            else:
                single_token_dict[i] = 1
        
        total_number_of_tokens = len(single_token_dict)

        for i in range(0, total_number_of_tokens-1):
            query = (vocab_lst[i] + " " + vocab_lst[i+1], (vocab_lst[i], vocab_lst[i+1]))
            if (query, lang_tag) in local_dict:
                continue
            p_occurences = len(re.findall(re.escape(query[0]), s))
            local_dict[(query, lang_tag)] = p_occurences
            all[(query, lang_tag)] = p_occurences
        return all

def LangId(filename, all_prob_en, all_prob_fr, all_prob_it, single_token_dict_en, single_token_dict_fr, single_token_dict_it):
    number = 0
    returned_list = []
    s = codecs.open(filename, 'r', 'iso-8859-1').read()
    sentence_list = re.findall(r'(?:.*)\s', s)
    p_queue_en = []
    p_queue_fr = []
    p_queue_it = []
    p_queue_all_en = []
    p_queue_all_fr = []
    p_queue_all_it = []



    for key in single_token_dict_en:
        bisect.insort(p_queue_en, (single_token_dict_en.get(key), key))
    for key in single_token_dict_fr:
        bisect.insort(p_queue_fr, (single_token_dict_fr.get(key), key))
    for key in single_token_dict_it:
        bisect.insort(p_queue_it, (single_token_dict_it.get(key), key))
    for key in all_prob_en:
        bisect.insort(p_queue_all_en, (all_prob_en.get(key), key))
    for key in all_prob_fr:
        bisect.insort(p_queue_all_fr, (all_prob_fr.get(key), key))
    for key in all_prob_it:
        bisect.insort(p_queue_all_it, (all_prob_it.get(key), key))


    for stc in sentence_list:
        vocab_lst = stc.split(' ')
        while '\n' in vocab_lst:
            vocab_lst.remove('\n')
        while '.' in vocab_lst:
            vocab_lst.remove('.')
        while ',' in vocab_lst:
            vocab_lst.remove(',')
        while '.\n' in vocab_lst:
            vocab_lst.remove('.\n')
        res_list = []
        local_dict = {}
        single_token_dict = {}
        all = []
        for i in vocab_lst:
            if i in local_dict:
                count = single_token_dict.get(i)
                count += 1
                single_token_dict[i] = count
            else:
                single_token_dict[i] = 1
        
        total_number_of_tokens = len(single_token_dict)

        for i in range(0, len(vocab_lst)-1):
            query = (vocab_lst[i] + " " + vocab_lst[i+1], (vocab_lst[i], vocab_lst[i+1]))
            if query in local_dict:
                continue
            p_occurences = len(re.findall(re.escape(query[0]), stc))
            local_dict[query] = p_occurences
            all.append(query)
        
        delta_en = 0.0
        delta_fr = 0.0
        delta_it = 0.0

        for key in all:
            if (key, "en") in all_prob_en:
                # calc = (all_prob_en.get((key, "en")) / (single_token_dict_en.get(key[1][0]) + len(single_token_dict_en))
                unigram_prob = adjusted_prob(p_queue_en, single_token_dict_en.get(key[1][0]))
                bigram_prob = adjusted_prob(p_queue_all_en, all_prob_en.get((key, "en")))
                calc = bigram_prob / unigram_prob
                delta_en += math.log(calc)

            elif key[1][0] in single_token_dict_en:
                unigram_prob = adjusted_prob(p_queue_en, single_token_dict_en.get(key[1][0]))
                bigram_prob = adjusted_prob(p_queue_all_en, 0)
                calc = bigram_prob / unigram_prob
                delta_en += math.log(calc)

            else: 
                unigram_prob = adjusted_prob(p_queue_en, 0)
                bigram_prob = adjusted_prob(p_queue_all_en, 0)
                calc = bigram_prob / unigram_prob
                delta_en += math.log(calc)
            
            if (key, "fr") in all_prob_fr:
                unigram_prob = adjusted_prob(p_queue_fr, single_token_dict_fr.get(key[1][0]))
                bigram_prob = adjusted_prob(p_queue_all_fr, 0)
                calc = bigram_prob / unigram_prob
                delta_fr += math.log(calc)

            elif key[1][0] in single_token_dict_fr:
                unigram_prob = adjusted_prob(p_queue_fr, single_token_dict_fr.get(key[1][0]))
                bigram_prob = adjusted_prob(p_queue_all_fr, 0)
                calc = bigram_prob / unigram_prob
                delta_fr += math.log(calc)
            else:
                unigram_prob = adjusted_prob(p_queue_fr, 0)
                bigram_prob = adjusted_prob(p_queue_all_fr, 0)
                calc = bigram_prob / unigram_prob
                delta_fr += math.log(calc)
            
            if (key, "it") in all_prob_it:
                unigram_prob = adjusted_prob(p_queue_it, single_token_dict_it.get(key[1][0]))
                bigram_prob = adjusted_prob(p_queue_all_it, all_prob_it.get((key, "it")))
                calc = bigram_prob / unigram_prob
                delta_it += math.log(calc)
            elif key[1][0] in single_token_dict_it:
                unigram_prob = adjusted_prob(p_queue_it, single_token_dict_it.get(key[1][0]))
                bigram_prob = adjusted_prob(p_queue_all_it, 0)
                calc = bigram_prob / unigram_prob
                delta_it += math.log(calc)
            else:
                unigram_prob = adjusted_prob(p_queue_it, 0)
                bigram_prob = adjusted_prob(p_queue_all_it, 0)
                calc = bigram_prob / unigram_prob
                delta_it += math.log(calc)

        res_list.append(("English", delta_en))
        res_list.append(("French", delta_fr))
        res_list.append(("Italian", delta_it))

        token = res_list[0]
        for i in res_list:
            if i[1] > token[1]:
                token = i
        returned_list.append(token[0])
        number += 1
    return returned_list


def adjusted_prob(p_queue, count):
    original_count = int()
    adj_count = int()
    if count == 0:
        for i in p_queue:
            if i[0] == 0:
                continue
            if i[0] == 1:
                original_count += 1
                continue
            if i[0] > 1:
                break
        return original_count/len(p_queue)
    
    else:
        for i in p_queue:
            new_count = count + 1
            if i[0] < count:
                continue
            if i[0] == count:
                original_count += 1
                continue 
            if i[0] == new_count:
                adj_count += 1
                continue
            if i[0] > new_count and adj_count == 0:
                new_count = i[0]
                adj_count += 1
                continue
            if i[0] > new_count and adj_count > 1:
                break
        if adj_count == 0:
            adj_count = original_count 
        return ((count + 1) * adj_count/original_count) / len(p_queue)
        
