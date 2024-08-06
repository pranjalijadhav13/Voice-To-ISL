# Voice to Indian Sign Language Translator
There is a common perception that even though deaf people use sign language as their main language, they can read texts fluently in their countries' oral language because their vision isn't hindered. Such perception does not correspond to reality. A sign language is a language on its own; people use different sign languages in different parts of the world. India has its own sign language by the name Indian Sign Language (ISL). As a language of its own, it has a set of grammar rules and specific sentence structure. These differences and the fact that signers learn their countries' written language as a second language are the main reason why deaf people can't fluently read written texts.

Example:- the sentence "I'm going home" in English can be "Home go" in sign language; for a person whose main language is sign language, all other words in the sentence are seen as noise that makes comprehension harder. To overcome this, we need a system for converting speech to sign language.

Sign language is a natural way of communication for challenged people with speaking and hearing disabilities. There have been various mediums available to translate or to recognize sign language and convert them to voice, but speech to sign language conversion systems have been rarely developed, this is due to the scarcity of any sign language corpus. Our project aims at creating ana English speech to Indian sign language translation system using NLP. Natural Language Processing, is broadly defined as the automatic manipulation of natural language, like speech and text, by software.

The proposed speech to Indian Sign language translation system consists of two parts :

1. **English speech to text translation**

   We have used the webkitSpeechRecognition interface of the Web Speech API.

2. **Text to ISL translation**

   The second part consists of a parsing module that parses the input English sentence to phrase structure grammar representation on which Indian sign language grammar rules are applied to reorder the words of the 	 English sentence (as the grammar of English language and Indian sign language is different). The elimination module eliminates unwanted words from the reordered sentence. Lemmatization is applied to convert the 	 words into the root form as the Indian sign language does not use the inflections of the words. All words of the sentence are then checked against the words in the dictionary containing videos representing each 	 of the words. The proposed system is innovative as the existing systems are limited to direct conversion of words into Indian sign language whereas our system aims to convert these sentences into Indian sign 			 language grammar in the real domain.
