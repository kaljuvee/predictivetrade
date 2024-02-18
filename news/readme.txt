# Preparing Environment

$ python3.9 -m venv myenv
$ source myenv/bin/activate
$ pip install -r requirements.txt
$ python news_item.py -s biotech

# Download spacy
python -m spacy download en_core_web_sm en_core_web_tr

# Open AI Fine Tuning using Open AI CLI

openai tools fine_tunes.prepare_data -f data/news.jsonl -q
openai api fine_tunes.create -t "data/news_prepared_train.jsonl" -v "data/news_prepared_valid.jsonl" --compute_classification_metrics --classification_positive_class " long" -m ada
openai api fine_tunes.results -i ft-ft-K7Hrh4sNyTAl6aaxypowMK0L > result.csv


echo "export OPENAI_API_KEY='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'" >> ~/.bashrc
source ~/.bashrc

echo $OPENAI_API_KEY
