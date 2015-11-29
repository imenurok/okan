import sys
import commands
import subprocess
import os.path

def cmd(cmd):
	p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	p.wait()
	stdout, stderr = p.communicate()
	return stdout.rstrip()

#labels
dirs = cmd("ls "+sys.argv[1])
labels = dirs.splitlines()

#make directries
cmd("mkdir images")

#copy images and make train.txt
imageDir = "images"
train = open('train.txt','w')
test = open('test.txt','w')
labelsTxt = open('labels.txt','w')

classNo=0
cnt = 0
#label = labels[classNo]
for label in labels:
	workdir = sys.argv[1]+"/"+label
	labelsTxt.write(label+"\n")
	startCnt=cnt
	imageCnt=0
	for image in range(100000):
		if (os.path.isfile(workdir+"/%05d" %image +".jpg")):
			imageCnt+=1
	length = imageCnt
	for image in range(length):
		imagepath = imageDir+"/image%07d" %cnt +".jpg"
		cmd("cp "+workdir+"/%05d" %image +".jpg "+imagepath)
		if cnt-startCnt < length*0.75:
			train.write(imagepath+" %d\n" % classNo)
		else:
			test.write(imagepath+" %d\n" % classNo)
		print imagepath 
		cnt += 1
	
	classNo += 1

train.close()
test.close()
labelsTxt.close()
