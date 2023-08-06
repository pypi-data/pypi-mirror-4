# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class demo3:
	pylToHtmlResult=""
	sessionDic=dict()
	def __init__(self,param,pyFile,session,headerInfo,lattedb):
		self.generate(param,pyFile,session,headerInfo,lattedb)

	def generate(self,param,pyFile,session,headerInfo,lattedb):
		self.pylToHtmlResult+=str("""<!DOCTYPE html>
<html>
	<head>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>Pylatte - Web framework based on Python3</title>
	
	<!-- favicon -->
	<link rel="shortcut icon" href="../pyl/favicon.ico" type="image/x-icon">
	<link rel="icon" href="../pyl/favicon.ico" type="image/x-icon">
	
	</head>
	
	<body>
	<div>
		<h3>Menu</h3>
		<ul>
			<li><a target="_self" href="../index">Main</a></li>
			<li><a target="_self" href="../demo1">Demo1</a></li>
			<li><a target="_self" href="../demo2">Demo2</a></li>
			<li><a target="_self" href="../demo3">Demo3</a></li>
			<li><a target="_self" href="../demo4">Demo4</a></li>
		</ul>
	</div>
""")

		import pylatte.database.DBMappingParser as pyLatteDBMappingParser

		contact = pyLatteDBMappingParser.pyLatteDBMappingParser()
		result = contact.queryForList("contact.founder")
		self.pylToHtmlResult+=str("""<div>
<h1>demo3</h1>
""")

		for (website,name,position,description) in result:
			self.pylToHtmlResult+=str("""		
		<a href=""")
			self.pylToHtmlResult+=str(website)
			self.pylToHtmlResult+=str(""" target="_black"><h3>""")
			self.pylToHtmlResult+=str(name)
			self.pylToHtmlResult+=str("""</h3></a>
		<p>
			<strong>""")
			self.pylToHtmlResult+=str(position)
			self.pylToHtmlResult+=str("""</strong>
		</p>
		<p>""")
			self.pylToHtmlResult+=str(description)
			self.pylToHtmlResult+=str("""</p>
		
""")

			pass
		self.pylToHtmlResult+=str("""</div>
</body>
</html>


""")
		self.sessionDic=session
		pass
	def getHtml(self):
		return self.pylToHtmlResult
		pass
	def getSession(self):
		return self.sessionDic
		pass
