# THIS CODE IS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING
# A TUTOR OR CODE WRITTEN BY OTHER STUDENTS - Jie Lin
# Python 3

#coding=utf-8
"""
@version: 1.0
@author: Jie Lin
@Mail: jlin246@emory.edu
@file: ICD_converter.py
@time: 11/09/2018 10:50am
@purpose: this python is to convert as many I10 to I9 one-to-many mappigs into one-to-one mappings as possible
@code environment: ubuntu 18.01
"""

import pandas as pd
import sys
import numpy as np
import random

txt_dir = "ICD9_frequencies.txt";

#convert a xlsx to a txt files
def convert_xlsx_to_txt(xlsx_path, sheet_name):
	xlsx = pd.read_excel(xlsx_path,sheet_name,header = None, index = None);
	with open(txt_dir,"w+") as outfile:
		outfile.write(xlsx.to_string());

	print(txt_dir+" has been converted. It is in the same path of this program")

#read data from txt file
def read_data(path_dir):
	df = pd.DataFrame(pd.read_csv(path_dir,sep="\s+",dtype = str));
	return df;

#read from I10 txt file
def readDataFromI10(I10_txt_path):
	data = pd.DataFrame(pd.read_csv(I10_txt_path,sep="\s+",names=['I10','I9','flags'],dtype=str));
	return data;

#a method for cleaning ICD9_frequencies_df
def clean_I9_frequency_data(df):
	# for testing
	#print(df);
	# change column names by the first row in the data
	column_names = list(df.iloc[0]);
	df.columns = column_names;
	#remove the first row and last row
	df = df.iloc[1:-1];

	# change all NaN to 0
	df.fillna(0, inplace = True);

	# change the data type of the columns beside ICD9CMCode to float
	column_names.remove("ICD9CMCode");
	# change data to float type for better calculating percentage
	df[column_names]=df[column_names].astype(float);
	# remove . from every data in column ICD9CMCode
	df["ICD9CMCode"] = df["ICD9CMCode"].str.replace('.','',regex=False);
	# calculate percentage from dx0 to dx24
	df.iloc[:,2:] = df.values[:,2:]/df.values[:,1,None]*100;
	# change back to integer for better looking data
	df[column_names]=df[column_names].astype(int);
	return df;

#delete no map entries
def deleteNoMapEntries(data):
	returnData = data.copy();
	for index, row in returnData.iterrows():
		if(row["flags"]=='11000'):
			returnData.drop(index,inplace = True);

	#for testing purpose
	#print("there are "+str(I10noEntryCounter)+" no mapping in I10 to I9");
	return returnData;

# cleaning I10_I9 data
def clean_I10_I9_data(df):
	#print(df);
	# delete no map entries
	df = deleteNoMapEntries(df);
	#print(df);
	# save all one to many entries
	e = df["I10"].value_counts();
	df = df[df["I10"].isin(e[e>1].index)]
	return df;

def transform_to_one_to_one(I10_to_I9_df,I9_frequency_df):
	result = "";
	# group by I10 column
	grouped = I10_to_I9_df.groupby(["I10"])
	#set index of I9_fre
	I9_frequency_df = I9_frequency_df.set_index("ICD9CMCode");

	for name,group in grouped:
		I9list = group["I9"].tolist();
		# to prevent if the entry does not exist in I9_frequency_df
		for I9_name in I9list[:]:
			try:
				I9_frequency_df.loc[I9_name];
			except KeyError:
				I9list.remove(I9_name);
		if(len(I9list)!=0):
			I9_frequency_data = I9_frequency_df.loc[I9list];
			I9_frequency_data["max_percentage"] = I9_frequency_data.values[:,1:].max(axis=1)
			I9_frequency_data["max_single_diagnosis"] = I9_frequency_data["TotalDiag"]* I9_frequency_data["max_percentage"];
			#print(I9_frequency_data["TotalDiag"].idxmax());
			optimal_I9_name = I9_frequency_data["max_single_diagnosis"].idxmax();
			result = result + name + " "+ optimal_I9_name+"\n";
		else:
			# if there is no match in frequency table, random select
			result = result + name + " " + random.choice(group["I9"].tolist())+"\n";

	return result;


def main_process(xlsx_path,sheet_name,I10_path,output_file_path):
	#convert a certain sheet in xlsn file to txt file
	#output file will be in the same folder as the program itself is in
	# the output of the txt will be named ICD9_frequencies.txt
	#convert_xlsx_to_txt(xlsx_path,sheet_name);
	
	#read datas
	I9_frequency_df = read_data(txt_dir);
	I10_to_I9_df = readDataFromI10(I10_path);
	I9_frequency_df =  clean_I9_frequency_data(I9_frequency_df);
	I10_to_I9_df =  clean_I10_I9_data(I10_to_I9_df);
	result = transform_to_one_to_one(I10_to_I9_df,I9_frequency_df);
	with open(output_file_path,'w+') as output_file:
		output_file.write(result);
	print("result file has created in "+output_file_path);

# main method
if __name__== "__main__":
	main_process(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]);