import os
import torch
from transformers import BartTokenizer, BartForConditionalGeneration
from flask import Flask, request
from datetime import datetime

print('Loading model...')
tokenizer = BartTokenizer.from_pretrained('./model')
model = BartForConditionalGeneration.from_pretrained('./model')


def save_backup(text):
    date = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    file_name = f"summarize_backup_{date}.txt"

    with open(os.path.join('data/summary_text_backups', file_name), "w") as fp:
        fp.write(text)


def make_summary(text):
    inputs_no_trunc = tokenizer(text, max_length=None, return_tensors='pt', truncation=False)

    chunk_start = 0
    chunk_end = tokenizer.model_max_length
    inputs_batch_lst = []
    while chunk_start <= len(inputs_no_trunc['input_ids'][0]):
        inputs_batch = inputs_no_trunc['input_ids'][0][chunk_start:chunk_end]
        inputs_batch = torch.unsqueeze(inputs_batch, 0)
        inputs_batch_lst.append(inputs_batch)
        chunk_start += tokenizer.model_max_length
        chunk_end += tokenizer.model_max_length

    summary_ids_lst = [model.generate(inputs, num_beams=4, max_length=100, early_stopping=True) for inputs in
                       inputs_batch_lst]

    summary_batch_lst = []
    for summary_id in summary_ids_lst:
        summary_batch = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
                         summary_id]
        summary_batch_lst.append(summary_batch[0])

    return '\n'.join(summary_batch_lst)


"""FLASK APP"""
app = Flask(__name__)


@app.route("/")
def index():
    return "Congratulations, it's a web app!"


@app.route('/summarize', methods=['POST', 'GET'])
def summarize():
    query = request.args.get('text')

    if isinstance(query, list):
        query = '\n\n'.join(query)

    print(query)
    sum_text = make_summary(query)
    save_backup(sum_text)

    summary = {}
    summary['summary'] = sum_text

    return summary


if __name__ == "__main__":
    app.run()
