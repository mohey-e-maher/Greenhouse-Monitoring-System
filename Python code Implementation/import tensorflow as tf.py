import tensorflow as tf
from sklearn.model_selection import train_test_split
import unicodedata
import re
import numpy as np
import os
import time
from unidecode import unidecode

path_to_file="/content/ara_.txt"
def unicode_to_ascii(s):
  return ''.join(c for c in unicodedata.normalize('NFD',s)if unicodedata.category(c)!='Mn')

def preprocess_sentence(w):
  w = unicode_to_ascii(w.lower().strip())
  w=re.sub(r"([?.!])",r"\1 ",w)
  w=re.sub(r'[" "]+'," ",w)
  w=re.sub(r"[^a-zA-Z-_?.]+"," ",w)
  w=w.rstrip().strip()
  w='<start> %s <end>' % w
  return w


def create_dataset(path, num_examples):
  lines = open(path, encoding='utf-8-sig').read().strip().split('\n')
  word_pairs=[[preprocess_sentence(w) for w in l.split('\t')] for l in lines[:num_examples]]
  print(len(lines))
  print(len(lines[:num_examples]))
  return word_pairs


class LanguageIndex():
    def __init__(self, lang):
        self.lang = lang
        self.word2idx = {}
        self.idx2word = {}
        self.vocab = set()
        self.create_index()

    def create_index(self):
        for phrase in self.lang:
            self.vocab.update(phrase.split(' '))
        self.vocab = sorted(self.vocab)
        self.word2idx['<pad>'] = 0
        for index, word in enumerate(self.vocab):
            self.word2idx[word] = index + 1
        for word, index in self.word2idx.items():
            self.idx2word[index] = word


def max_length(tensor):
  return max(len(t)for t in tensor)


def load_dataset(path, num_examples):
    pairs = create_dataset(path, num_examples)
    inp_lang = LanguageIndex(sp for en, sp in pairs)
    targ_lang = LanguageIndex(en for en, sp in pairs)
    input_tensor = [[inp_lang.word2idx[s] for s in sp.split(' ')] for en, sp in pairs]
    target_tensor = [[targ_lang.word2idx[s] for s in en.split(' ')] for en, sp in pairs]
    max_length_inp, max_length_tar = max_length(input_tensor), max_length(target_tensor)
    input_tensor = tf.keras.preprocessing.sequence.pad_sequences(input_tensor, maxlen=max_length_inp, padding='post')
    target_tensor = tf.keras.preprocessing.sequence.pad_sequences(target_tensor, maxlen=max_length_tar, padding='post')
    return input_tensor, target_tensor, inp_lang, targ_lang, max_length_inp, max_length_tar


num_examples = 30000
input_tensor, target_tensor, inp_lang, targ_lang, max_length_inp, max_length_targ = load_dataset(path_to_file, num_examples)
input_tensor_train, input_tensor_val, target_tensor_train, target_tensor_val = train_test_split(input_tensor, target_tensor, test_size=0.2)


len(input_tensor_train), len(target_tensor_train),len(input_tensor_val),len(target_tensor_val)

import torch
from transformers import MBartForConditionalGeneration, MBartTokenizer


model_name="facebook/mbart-large-50-many-to-many-mmt"
tokenizer =MBartTokenizer.from_pretrained(model_name)
model = MBartForConditionalGeneration.from_pretrained(model_name)

def translate_with_mbart(sentence, source_lang, target_lang):
    input_text = f"{source_lang}:{sentence}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)
    translated = model.generate(input_ids, decoder_start_token_id=tokenizer.lang_code_to_id[target_lang])
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

source_lang = "ar_AR"
target_lang = "en_XX"
example_sentence = "هل أنت موجود في المنزل؟"
translated_sentence = translate_with_mbart(example_sentence, source_lang, target_lang)
print(f"Input: {example_sentence}")
print(f"Translation: {translated_sentence}")
