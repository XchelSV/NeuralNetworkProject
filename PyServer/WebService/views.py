# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import JsonResponse
from django.core import serializers

import json
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
	min_num = 0
	max_num = 0
	for idy,line in enumerate(normalize_file):
		temp_line = [ x.strip() for x in line.split('\t')]
		for idx,num in enumerate(temp_line):
			if idy == 0 and idx == 0:
				min_num = float(num)
				max_num = float(num)
			if idx < len(temp_line)-1:
				if float(num)>max_num:
					max_num = float(num)
				if float(num)<min_num:
					min_num = float(num)
	normalize_file.close()

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
				temp_new_line = temp_new_line+str(float( (float(num)-min_num)/(max_num-min_num) ))+'\t'
		normalize_end_file.write(temp_new_line)

	normalize_end_file.close()
	normalize_file.close()
	#End for Normalization

	data = Orange.data.Table("normalize_test_data")
	data.shuffle()

	nn = Orange.classification.NNClassificationLearner(hidden_layer_sizes=(layers), activation=func_act, learning_rate_init=learning_rate, max_iter=epoch, momentum=momentum)
	res = Orange.evaluation.CrossValidation(data, [nn], k=k_folds)
	# sgd, lbfgs, Adam
	# relu , identity, logistic, tanh

	z = [(round(Orange.evaluation.scoring.AUC(res)[0],3)),(round(Orange.evaluation.scoring.CA(res)[0],3)),(round(Orange.evaluation.scoring.F1(res,average="weighted")[0],3)),(round(Orange.evaluation.scoring.Precision(res,average="weighted")[0],3)),(round(Orange.evaluation.scoring.Recall(res,average="weighted")[0],3))]

	print(z)
	
	response_data = {}
	response_data['AUC']= z[0]
	response_data['CA']= z[1]
	response_data['F1']= z[2]
	response_data['Precision']= z[3]
	response_data['Recall']= z[4]

	return HttpResponse(JsonResponse(response_data), content_type='application/json')
