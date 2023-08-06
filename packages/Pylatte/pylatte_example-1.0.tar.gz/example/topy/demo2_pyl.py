# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class demo2:
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
		<h1>Demo2</h1>
		<h2>파일 업로드 Test</h2>
		<p>웹사이트의 이미지을 업로드하여 아래의 이미지를 변경한다.</p>
		<div>
			<form id="fileForm" method="post" enctype="multipart/form-data"
				action="/faviconUpload">
				<input type="file" name="file1" />
				<button type="submit" name="submit" value="submit-value">Submit</button>
			</form>
		</div>
		<img src='/image/log.jpeg' />


	</div>

</div>



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
