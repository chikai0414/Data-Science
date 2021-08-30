import numpy as np 
import pandas as pd
import keras
from keras.layers import Embedding, LSTM, concatenate, Dense,Bidirectional


if __name__ == "__main__":
	data = pd.read_csv('train.csv')
	data1 = pd.read_csv('test.csv')
	MAX_NUM_WORDS = 10000
	tokenizer = keras.preprocessing.text.Tokenizer(num_words=MAX_NUM_WORDS)

	x=data["Headline"].str.replace(',', '') 
	d=x.str.replace(',', ' ') 
	d=d.str.replace(':', ' ') 
	d=d.str.replace('.', ' ') 
	d=d.str.replace('!', ' !')
	d=d.str.replace('?', ' ?')
	d=d.str.split()
	tokenizer.fit_on_texts(d)
	data_in_word=tokenizer.texts_to_sequences(d)


	MAX_SEQUENCE_LENGTH = 20
	data_in_word = keras \
	    .preprocessing \
	    .sequence \
	    .pad_sequences(data_in_word, 
	                   maxlen=MAX_SEQUENCE_LENGTH)
	xx=data1["Headline"].str.replace(',', '')
	xx=xx.str.replace(',', ' ') 
	xx=xx.str.replace(':', ' ') 
	xx=xx.str.replace('.', ' ') 
	xx=xx.str.replace('!', ' !')
	xx=xx.str.replace('?', ' ?') 
	xx=xx.str.split()

	data_in_word1=tokenizer.texts_to_sequences(xx)

	data_in_word1 = keras \
	    .preprocessing \
	    .sequence \
	    .pad_sequences(data_in_word1, 
	                   maxlen=MAX_SEQUENCE_LENGTH)
	new_model = keras.models.load_model('model_k.h5')
	predictions = new_model.predict(data_in_word1)
	IDX=np.array(range(1,228))
	df = pd.DataFrame(list(zip(*[IDX,np.array(predictions).reshape(-1)])),columns=["ID", "Label"])
	df.to_csv('309512010.csv', index=False)
