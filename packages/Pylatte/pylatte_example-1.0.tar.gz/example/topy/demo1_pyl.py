# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class demo1:
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
	<div>
			<div>
			<h1>Demo1</h1>
			<h2>GET/POST Test</h2>
			<h3>GET request 테스트</h3>
			<p>get 요청은 url뒤에 ?name=변수를 붙여서 확인하도록 함.</p>
			<h3>POST request 테스트</h3>
			<form name="form" method="post" action="../demo1">
				<p>
					<input type="text" name="name">
					<input type="submit" value="CLICK">
				</p>
			</form>
			<p>Get or Post :
""")

		if param=={} :
			pass

		elif "name" in param:
			self.pylToHtmlResult+=str("""	""")
			self.pylToHtmlResult+=str(param['name'])
			self.pylToHtmlResult+=str("""</p>
""")

			pass
		self.pylToHtmlResult+=str("""</p>
			<h2>Session Test</h2>
			<form name="form" method="post" action="../demo1">
				<p>
					<input type="text" name="sessionValue">
					<input type="submit" value="CLICK">
				</p>
			</form>
			<p>Sessio Value :
""")

		if param=={} :
			pass

		elif "sessionValue" in param:
			session['sessionValue']=param['sessionValue']
			pass

		if "sessionValue" in session:
			self.pylToHtmlResult+=str("""	""")
			self.pylToHtmlResult+=str(session['sessionValue'])
			self.pylToHtmlResult+=str("""</p>
""")

			pass
		self.pylToHtmlResult+=str("""</p>
			<h3>HeaderInfo['PATH_INFO']</h3>
			<p>""")
		self.pylToHtmlResult+=str(headerInfo['PATH_INFO'])
		self.pylToHtmlResult+=str("""</p>
			<h3>HeaderInfo['HTTP_ACCEPT']</h3>
			<p>""")
		self.pylToHtmlResult+=str(headerInfo['HTTP_ACCEPT'])
		self.pylToHtmlResult+=str("""</p>
			<h3>HeaderInfo['SERVER_NAME']</h3>
			<p>""")
		self.pylToHtmlResult+=str(headerInfo['SERVER_NAME'])
		self.pylToHtmlResult+=str("""</p>
			<h3>HeaderInfo['HTTP_USER_AGENT']</h3>
			<p>""")
		self.pylToHtmlResult+=str(headerInfo['HTTP_USER_AGENT'])
		self.pylToHtmlResult+=str("""</p>
			</div><!--/content-primary -->


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
