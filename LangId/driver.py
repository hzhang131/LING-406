import letterLangId
import wordLangId
import wordLangId2

letterLangId.driver(["LangId.train.English", "LangId.train.French", "LangId.train.Italian"], "LangId.test", "LangId.sol")
wordLangId.driver(["LangId.train.English", "LangId.train.French", "LangId.train.Italian"], "LangId.test", "LangId.sol")
wordLangId2.driver(["LangId.train.English", "LangId.train.French", "LangId.train.Italian"], "LangId.test", "LangId.sol")
print("Done!")