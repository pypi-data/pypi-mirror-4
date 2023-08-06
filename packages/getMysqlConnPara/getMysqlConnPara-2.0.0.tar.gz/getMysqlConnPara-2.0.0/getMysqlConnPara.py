# -*- coding: utf-8 -*-
#檔名：getMysqlConnPara.py
#version:1.0.1
#change log:修正return，改為輸出dict型態

import os

def getMysqlConnPara(pathString):
	string ={'user':'',
		'password':'',
		'host':'',
		'database':''}
	i = 0
	start = 0
	stringCom = ''
	try:#如果檔案不存在，如指定的檔案不存在，回報「指定檔案路徑錯誤或不存在」	
		with open(pathString)as data:
			while 1:
				line = data.readline()
				#line是矩陣
				if not line :#line == EOF
					break
				else:
					#conf檔案允許加入註解，一行的首字如果為 # ，表示註解，忽略不處理
					if line[0] == "#":
						continue
					else:
						#參數不足，如果不足四個參數，回報「參數不足」
						if str(line).find("=") > 0:
							#print str(line).find("=")
							#格式錯誤，例如passwod='123456'，回報「格式錯誤」
							index = str(line).find("=", start)
							stringCom = str(line[0:index])
							if not (stringCom == "host" or stringCom == "user" or stringCom == "password" or stringCom == "database") :
								print "Error! Format error!"
								print stringCom
								break
							if index > 0 :
								i = i+1
							#不是空白行時
							if not line == "\n" :
								line = line.split()[0].split('=')
								string[line[0]] = line[1]
						elif str(line).find("=") < 0 and len(line) > 1:
							print line+" is not right format parameter , please check again."
							continue
			if i < 4:
				print('Not enough parameter,please check again.')
				return ''
			elif i > 4:
				print('too much parameter,please check again.')
				return ''
		#因加上逗號之故，所以要去除掉最前面的逗號才開始列印字串
		#string = string[1:len(string)]
		return string
	except IOError:
		print('file not found,or have a error file path.')
