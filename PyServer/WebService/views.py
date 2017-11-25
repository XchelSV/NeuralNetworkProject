# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

import json
import random
import math   # This will import math module
import Orange

@csrf_exempt
def backPropagation_view(request):

	raw_layers = str(request.POST.get("capas",""))
	func_act = str(request.POST.get("funcion",""))
	learning_rate = float(request.POST.get("tasa",""))
	epoch = int(request.POST.get("epocas",""))
	momentum = float(request.POST.get("momentum",""))
	k_folds = int(request.POST.get("kvalue",""))
	layers = [ int(x.strip()) for x in raw_layers.split(',')]

	#Create Tab file from Txt File
	file_path = str(request.POST.get("file",""))
	file = open(file_path, "r")
	data_num = file.readline()
	attr_num = int(file.readline())
	class_num = int(file.readline())
	attr_arr = ''
	type_attr_arr = ''
	select_class_arr = ''
	for i in range(attr_num):
		attr_arr = attr_arr+'Atributo'+str(i)+'\t'
		type_attr_arr = type_attr_arr+'c\t' 
		select_class_arr = select_class_arr+'\t'
	for i in range(class_num):
		attr_arr = attr_arr+'Clase'+str(i)+'\t'
		type_attr_arr = type_attr_arr+'d\t'
		select_class_arr = select_class_arr+'c\t'
	
	attr_arr = attr_arr+'\n'
	type_attr_arr = type_attr_arr+'\n' 
	select_class_arr = select_class_arr+'\n'

	dest_file = open('/home/xchel/Documentos/orange3/Orange/datasets/test_data.tab', "w")
	dest_file.write(attr_arr)
	dest_file.write(type_attr_arr)
	dest_file.write(select_class_arr)
	for idx,line in enumerate(file): 
		temp_line = line.replace(',','\t')
		dest_file.write(temp_line)
	dest_file.close()
	file.close()
	# End for Create Tab File Script

	#Normalization Min-Max 0-1
	normalize_file = open('/home/xchel/Documentos/orange3/Orange/datasets/test_data.tab', "r")
	line1 = normalize_file.readline()
	line2 = normalize_file.readline()
	line3 = normalize_file.readline()
	min_num = []
	max_num = []
	for idy,line in enumerate(normalize_file):
		temp_line = [ x.strip() for x in line.split('\t')]
		for idx,num in enumerate(temp_line):
			
			if idx < len(temp_line)-1:
				if idy == 0:
					min_num.append(float(num))
					max_num.append(float(num))

				if float(num)> max_num[idx]:
					max_num[idx] = float(num)
				if float(num)<min_num[idx] :
					min_num[idx] = float(num)
	normalize_file.close()
	#print(min_num)
	#print(max_num)

	normalize_file = open('/home/xchel/Documentos/orange3/Orange/datasets/test_data.tab', "r")
	normalize_end_file = open('/home/xchel/Documentos/orange3/Orange/datasets/normalize_test_data.tab', "w")
	line1 = normalize_file.readline()
	line2 = normalize_file.readline()
	line3 = normalize_file.readline()
	normalize_end_file.write(line1)
	normalize_end_file.write(line2)
	normalize_end_file.write(line3)
	for idy,line in enumerate(normalize_file):
		temp_new_line = ''
		temp_line = [ x.strip() for x in line.split('\t')]
		for idx,num in enumerate(temp_line):
			if idx == len(temp_line)-1:
				temp_new_line = temp_new_line+num+'\n'
			else:
				temp_new_line = temp_new_line+str(float( (float(num)-min_num[idx])/(max_num[idx]-min_num[idx]) ))+'\t'
		normalize_end_file.write(temp_new_line)

	normalize_end_file.close()
	normalize_file.close()
	#End for Normalization

	data = Orange.data.Table("normalize_test_data")
	data.shuffle()

	nn = Orange.classification.NNClassificationLearner(hidden_layer_sizes=(layers), activation=func_act, learning_rate_init=learning_rate, max_iter=epoch, momentum=momentum)
	
	#CrossValidation Fold by fold
	normalize_end_file = open('/home/xchel/Documentos/orange3/Orange/datasets/normalize_test_data.tab', "r")
	line1 = normalize_end_file.readline()
	line2 = normalize_end_file.readline()
	line3 = normalize_end_file.readline()
	len_file = len(normalize_end_file.readlines())
	normalize_end_file.close()
	
	normalize_end_file = open('/home/xchel/Documentos/orange3/Orange/datasets/normalize_test_data.tab', "r")	
	line1 = normalize_end_file.readline()
	line2 = normalize_end_file.readline()
	line3 = normalize_end_file.readline()

	len_datasets = math.ceil(len_file/k_folds)
	lines_arr = normalize_end_file.readlines()
	random.shuffle(lines_arr)
	index_limits = []
	folds_results = []

	for i in range(k_folds):
		index_limits.append( (i*len_datasets)+(len_datasets-1) )
	
	for i in range(k_folds):
		train_fold_data = open('/home/xchel/Documentos/orange3/Orange/datasets/train_fold_data.tab', "w")
		test_fold_data = open('/home/xchel/Documentos/orange3/Orange/datasets/test_fold_data.tab', "w")
		train_fold_data.write(line1)
		train_fold_data.write(line2)
		train_fold_data.write(line3)
		test_fold_data.write(line1)
		test_fold_data.write(line2)
		test_fold_data.write(line3)
		for j in range(len_file):
			if j >= (i*len_datasets) and j <= index_limits[i]:
				test_fold_data.write(lines_arr[j])
			else:
				train_fold_data.write(lines_arr[j])		
		train_fold_data.close()
		test_fold_data.close()

		train_data = Orange.data.Table("train_fold_data")
		test_data = Orange.data.Table("test_fold_data")
		folds_results.append( round(Orange.evaluation.scoring.CA(Orange.evaluation.testing.TestOnTestData(train_data, test_data, [nn]))[0], 3 ))
	
	normalize_end_file.close()
	#End Cross Validation Fold by Fold

	#Global CrossValidation
	res = Orange.evaluation.CrossValidation(data, [nn], k=k_folds)
	# sgd, lbfgs, Adam
	# relu , identity, logistic, tanh
	z = [(round(Orange.evaluation.scoring.AUC(res)[0],3)),(round(Orange.evaluation.scoring.CA(res)[0],3)),(round(Orange.evaluation.scoring.F1(res,average="weighted")[0],3)),(round(Orange.evaluation.scoring.Precision(res,average="weighted")[0],3)),(round(Orange.evaluation.scoring.Recall(res,average="weighted")[0],3))]
	
	response_data = {}
	response_data['CA']= z[1]
	response_data['folds'] = folds_results

	return HttpResponse(JsonResponse(response_data), content_type='application/json')
