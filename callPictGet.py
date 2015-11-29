import subprocess

linelist=[
"rm -rf Timeline",
"javac PictGet.java -classpath .:./twitter4j-core-4.0.4.jar",
"java -classpath .:./twitter4j-core-4.0.4.jar PictGet"
]

for line in linelist:
	subprocess.call(line,shell=True)
