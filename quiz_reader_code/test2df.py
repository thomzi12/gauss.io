#Author: Kevin Vo
#This script converts markdown, pdf and word docs
#into a dataframe --> column 1: unique id
#column 2: question as a string

import pandas as pd
import PyPDF2
import glob
import slate


def makeQuestion(pageString):
	listOfQuestions = list()
	question = ''
	for word in pageString:
		if ("Problem" in word):
			if(question != ''):
				listOfQuestions.append(question)
			question = ''
		else:
			question = question + word
	listOfQuestions.append(question)
	return listOfQuestions

def cleanString(pageString):
	pageString = pageString.split('\n')
	pageString = [s.replace('\t', ' ') for s in pageString]
	pageString = filter(lambda a: a != '', pageString)
	pageString = [s.strip() for s in pageString]
	pageString = filter(lambda a: a != '', pageString)
	return pageString

def pdf2DF(pdfFile):
	#This is to get the number of pages
	pdfFileObj = open(pdfFile, 'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
	totalPages = pdfReader.numPages

	with open(pdfFile) as f:
		doc = slate.PDF(f)

	#Each page is one gigantic string
	for i in range(0, totalPages):
		pageString = doc[i]
		pageString = cleanString(pageString)
		listOfQuestions = makeQuestion(pageString)
		
	dataDict = dict()
	dataDict['id'] = list(range(len(listOfQuestions)))
	dataDict['question'] = listOfQuestions
	df = pd.DataFrame(dataDict)
	return df




	

