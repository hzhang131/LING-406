import codecs
import re
import bisect

def driver(filename_lst, filename, sol):
    """
    driver code for the letter-bigram language identification code.
    """

    all_prob_en = {}
    all_prob_fr = {}
    all_prob_it = {}
    prob_list = letterLangId(filename_lst, all_prob_en, all_prob_fr, all_prob_it)
    lst = LangId("LangId.test", prob_list[0], prob_list[1], prob_list[2])
    out_str = ""
    for i in lst:
        out_str += i
        out_str += "\n"
    codecs.open("letterLangId.out", "w").write(out_str)
    sol_ = codecs.open(sol, "r").read()
    count = 0
    errorCount = 0
    res_list = re.findall(r'\s(:?English|French|Italian)\s', sol_)
    for i in range(0, len(res_list)):
        count += 1
        if res_list[i] != lst[i]:
            errorCount += 1
    print("Accuracy of letter-bigram model is: ", (count - errorCount)/count * 100.0, "%.")
    print("Output saved to letterLangId.out")
    # print("Total: ", count)
    # print("Missed: ", errorCount)
    return

def letterLangId(filename_lst, all_prob_en, all_prob_fr, all_prob_it):
    """
    Implements a letter bigram model for language identification...
    (With Laplacian Smoothing)
    """
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
        # calculate probs of letter bigrams. includes apostrophes but ignores comma and period.
        s = codecs.open(file, 'r', 'iso-8859-1').read()
        sentence_list = re.findall(r'(?:.*)\s', s)
        
        for i in sentence_list:
            output_str += i
            output_str += "\n"
        if lang_tag == "en":
            all_prob_en = letterprob(sentence_list, lang_tag, s)
        if lang_tag == "fr":
            all_prob_fr = letterprob(sentence_list, lang_tag, s)
        if lang_tag == "it":
            all_prob_it = letterprob(sentence_list, lang_tag, s)
    return [all_prob_en, all_prob_fr, all_prob_it]

def letterprob(lst, lang_tag, s):
    single_token_dict = {}
    local_dict = {}
    all = {} 
    # calculate number of tokens.
    for stc in lst:
        for i in range(0, len(stc)):
            if stc[i] == "." or stc[i] == " " or stc[i] == "," or stc[i] == "\"" or stc[i] == ":" or stc[i] == "\n":
                continue
            if stc[i] not in single_token_dict:
                single_token_dict[stc[i]] = 1
                continue
            if stc[i] in single_token_dict:
                single_token_dict[stc[i]] = single_token_dict.get(stc[i]) + 1
            
    total_tokens_seen = len(single_token_dict)
    
    for i in range(0, len(s)-1):
        if s[i] == "." or s[i] == " " or s[i] == "," or s[i] == "\"" or s[i] == ":" or s[i] == "\n":
            continue
        if s[i+1] == "." or s[i+1] == " " or s[i+1] == "," or s[i+1] == "\"" or s[i+1] == ":" or s[i+1] == "\n":
            continue
            
        query = s[i] + s[i+1]
        if (query, lang_tag) in local_dict:
            continue
        p_occurences = len(re.findall(re.escape(query), s))
        local_dict[(query, lang_tag)] = p_occurences
    # print(local_dict)
    for key in local_dict:
        prob = (local_dict.get(key) + 1) / (single_token_dict.get(key[0][0]) + total_tokens_seen)
        all[key] = prob
    return all

def LangId(filename, all_prob_en, all_prob_fr, all_prob_it):
    """
    identify languages line by line...
    """
    number = 0
    returned_list = []
    s = codecs.open(filename, 'r', 'iso-8859-1').read()
    sentence_list = re.findall(r'(?:.*)\s', s)
    for stc in sentence_list:
        # print(stc)
        res_list = []
        single_token_dict = {}
        local_dict = {}
        all = {}
        for i in range(0, len(stc)):
            if stc[i] == "." or stc[i] == " " or stc[i] == "," or stc[i] == "\"" or stc[i] == ":" or stc[i] == "\n":
                continue
            if stc[i] not in single_token_dict:
                single_token_dict[stc[i]] = 1
                continue
            if stc[i] in single_token_dict:
                single_token_dict[stc[i]] = single_token_dict.get(stc[i]) + 1
        # compare with en.
        total_tokens_seen = len(single_token_dict)
    
        for i in range(0, len(stc)-1):
            if stc[i] == "." or stc[i] == " " or stc[i] == "," or stc[i] == "\"" or stc[i] == ":" or stc[i] == "\n":
                continue
            if stc[i+1] == "." or stc[i+1] == " " or stc[i+1] == "," or stc[i+1] == "\"" or stc[i+1] == ":" or stc[i+1] == "\n":
                continue
            query = stc[i] + stc[i+1]
            if query in local_dict:
                continue
            p_occurences = len(re.findall(re.escape(query), stc))
            local_dict[query] = p_occurences

        for key in local_dict:
            prob = (local_dict.get(key) + 1) /(single_token_dict.get(key[0]) + total_tokens_seen)
            all[key] = prob
    
        delta_en = 1.0
        delta_fr = 1.0
        delta_it = 1.0
        
        for key in all:
            if (key, "en") in all_prob_en:
                delta_en *= all_prob_en.get((key, "en"))
            else:
                delta_en *= 1/total_tokens_seen
            
            if (key, "fr") in all_prob_fr:
                delta_fr *= all_prob_fr.get((key, "fr"))
            else:
                delta_fr *= 1/total_tokens_seen

            if (key, "it") in all_prob_it:
                delta_it *= all_prob_it.get((key, "it"))
            else:
                delta_it *= 1/total_tokens_seen

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
