import os
import email
import pandas as pd
from string import punctuation
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import re
from loguru import logger


stop_words = set(stopwords.words("english"))


class StructureEnron(object):
    @staticmethod
    def count_dirs(dirs):
        for d in dirs:
            folders = 0
            for _, dirnames, filenames in os.walk(d):
                folders += len(dirnames)
            print("There are", folders, "folders in the Ham and Spam Directory")

    @staticmethod
    def getlist(directory):
        mylist = []
        for directory, subdirectory, filenames in os.walk(directory):
            for filename in filenames:
                with open(
                    os.path.join(directory, filename), "r", encoding="latin-1"
                ) as f:
                    data = f.read()
                b = email.message_from_string(data)
                if b.is_multipart():
                    for payload in b.get_payload():
                        if payload.is_multipart():
                            for payload1 in payload.get_payload():
                                mylist.append(payload1.get_payload())
                        else:
                            mylist.append(payload.get_payload())
                else:
                    mylist.append(b.get_payload())
        return mylist

    @staticmethod
    def create_df(hamlist, spamlist):
        ham = pd.DataFrame(hamlist, columns=["email"])
        ham["target"] = 0
        spam = pd.DataFrame(spamlist, columns=["email"])
        spam["target"] = 1
        all_emails = pd.concat([ham, spam])
        all_emails = all_emails.sample(frac=1).reset_index(drop=True)
        return all_emails

    @classmethod
    def clean_regex(cls, m):
        m = re.sub(
            r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", "", str(m)
        )  # email addresses
        m = re.sub(
            r"(http|https|ftp)://[a-zA-Z0-9\\./]+", " ", str(m)
        )  # http/url regex
        m = re.sub(r"\d+", "", str(m))  # numbers
        m = re.sub(r"<[^<]+?>", "", str(m))  # html <tags>
        m = m.replace(r"[^a-zA-Z]", "")  # non alphanumerics
        m = m.replace("nbsp", "")  # common in unprocessed spam files, new html
        m = m.translate(str.maketrans("", "", punctuation))  # remove punctuation
        m = m.lower()  # lower case
        return m

    @classmethod
    def clean_column(cls, df, col_name):
        df[col_name] = df[col_name].apply(cls.clean_regex)
        df[col_name] = df[col_name].apply(
            lambda x: " ".join([item for item in x.split() if item not in stop_words])
        )
        df[col_name] = df[col_name].apply(
            lambda x: " ".join([item for item in x.split() if 3 <= len(item) <= 15])
        )
        lem = WordNetLemmatizer()
        df[col_name] = df[col_name].apply(
            lambda x: " ".join([lem.lemmatize(word, pos="v") for word in x.split()])
        )
        df[col_name] = df[col_name].apply(
            lambda x: " ".join([lem.lemmatize(word, pos="n") for word in x.split()])
        )
        return df


if __name__ == "__main__":
    logger.info("Started enron data processing")
    hamdir = "spam"
    spamdir = "ham"
    dirs = [hamdir, spamdir]
    hamlist = StructureEnron.getlist(hamdir)
    spamlist = StructureEnron.getlist(spamdir)
    logger.success("fetched the list of ham and spam successful")
    all_emails = StructureEnron.create_df(hamlist, spamlist)
    logger.success("all emails fetched succcessful")
    all_emails_clean: pd.DataFrame = StructureEnron.clean_column(all_emails, "email")
    logger.success("cleaned the data successful")
    all_emails_clean.to_csv("preprocessed_data.csv", index=False)
    logger.success("saved the data to preprocessed_data")
