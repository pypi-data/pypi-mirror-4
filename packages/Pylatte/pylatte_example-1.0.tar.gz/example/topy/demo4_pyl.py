# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class demo4:
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
<h1>Demo4</h1>
<h2>SQL Test</h2>
""")

		import pylatte.database.DBMappingParser as pyLatteDBMappingParser

		contact = pyLatteDBMappingParser.pyLatteDBMappingParser()
		result = contact.queryForList("demo.select")
		self.pylToHtmlResult+=str("""<form id="fileForm" method="post" action="/sql">
<fieldset>
	<legend>select uid,name from test</legend>
					
""")

		for (uid,name) in result:
			self.pylToHtmlResult+=str("""<input type='radio' name='uid' id='""")
			self.pylToHtmlResult+=str(uid)
			self.pylToHtmlResult+=str("""' value='""")
			self.pylToHtmlResult+=str(uid)
			self.pylToHtmlResult+=str("""' />
<label >""")
			self.pylToHtmlResult+=str(uid)
			self.pylToHtmlResult+=str(""" : """)
			self.pylToHtmlResult+=str(name)
			self.pylToHtmlResult+=str("""</label>
""")

			pass
		self.pylToHtmlResult+=str("""</fieldset>

<div>
    <label for="name">name:</label>
    <input type="text" name="name" id="name" value=""  />
</div>
<label >Shipping method:</label>
<select name="method" id="select-choice-min" data-mini="true">
   <option value="insert">insert</option>
   <option value="update">update</option>
   <option value="delete">delete</option>
</select> 
<button type="submit" name="submit" value="submit-value">Submit</button>
</from>
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
