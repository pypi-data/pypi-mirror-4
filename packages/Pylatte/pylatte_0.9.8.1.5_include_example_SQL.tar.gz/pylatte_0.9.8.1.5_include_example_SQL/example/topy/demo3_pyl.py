# -*- coding: utf-8 -*- 
import Pylatte.WebServer.formFile as formFile
class demo3:
	pylToHtmlResult=""
	sessionDic=dict()
	def __init__(self,param,pyFile,session,headerInfo,lattedb):
		self.generate(param,pyFile,session,headerInfo,lattedb)

	def generate(self,param,pyFile,session,headerInfo,lattedb):
		self.pylToHtmlResult+=str("""<!DOCTYPE html>""")
		self.pylToHtmlResult+=str("""
<html>""")
		self.pylToHtmlResult+=str("""
	<head>""")
		self.pylToHtmlResult+=str("""
	<meta name="viewport" content="width=device-width, initial-scale=1">""")
		self.pylToHtmlResult+=str("""
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">""")
		self.pylToHtmlResult+=str("""
	<title>""")
		self.pylToHtmlResult+=str("""Pylatte""")
		self.pylToHtmlResult+=str(""" -""")
		self.pylToHtmlResult+=str(""" Web""")
		self.pylToHtmlResult+=str(""" framework""")
		self.pylToHtmlResult+=str(""" based""")
		self.pylToHtmlResult+=str(""" on""")
		self.pylToHtmlResult+=str(""" Python3""")
		self.pylToHtmlResult+=str("""</title>""")
		self.pylToHtmlResult+=str("""
	
	<!-- favicon -->""")
		self.pylToHtmlResult+=str("""
	<link rel="shortcut icon" href="../pyl/favicon.ico" type="image/x-icon">""")
		self.pylToHtmlResult+=str("""
	<link rel="icon" href="../pyl/favicon.ico" type="image/x-icon">""")
		self.pylToHtmlResult+=str("""

	<!-- Include required JS files -->""")
		self.pylToHtmlResult+=str("""
	<script type="text/javascript" src="../pyl/syntaxhighlighter/js/xregexp.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	<script type="text/javascript" src="../pyl/syntaxhighlighter/js/shCore.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	 
	<!--
	    At least one brush, here we choose JS. You need to include a brush for every
	    language you want to highlight
	-->""")
		self.pylToHtmlResult+=str("""
	<script type="text/javascript" src="../pyl/syntaxhighlighter/lang/shBrushXml.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	<script type="text/javascript" src="../pyl/syntaxhighlighter/lang/shBrushBash.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	 
	<!-- Include *at least* the core style and default theme -->""")
		self.pylToHtmlResult+=str("""
	<link href="../pyl/syntaxhighlighter/css/shCore.css" rel="stylesheet" type="text/css" />""")
		self.pylToHtmlResult+=str("""
	<link href="../pyl/syntaxhighlighter/css/shThemeDefault.css" rel="stylesheet" type="text/css" />""")
		self.pylToHtmlResult+=str("""
	
	
	
	<link rel="stylesheet"  href="../pyl/css/jquery.mobile-1.2.0.css"/>""")
		self.pylToHtmlResult+=str("""
	<link rel="stylesheet"  href="../pyl/css/jqm-docs.css"/>""")
		self.pylToHtmlResult+=str("""
	
	<script src="../pyl/js/jquery.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	<script src="../pyl/js/jqm-docs.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	<script src="../pyl/js/jquery.mobile.themeswitcher.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	<script src="../pyl/js/jquery.mobile-1.2.0.min.js">""")
		self.pylToHtmlResult+=str("""</script>""")
		self.pylToHtmlResult+=str("""
	
	<script type="text/javascript">""")
		self.pylToHtmlResult+=str("""

	  var""")
		self.pylToHtmlResult+=str(""" _gaq""")
		self.pylToHtmlResult+=str(""" =""")
		self.pylToHtmlResult+=str(""" _gaq""")
		self.pylToHtmlResult+=str(""" ||""")
		self.pylToHtmlResult+=str(""" [];""")
		self.pylToHtmlResult+=str("""
	  _gaq.push(['_setAccount',""")
		self.pylToHtmlResult+=str(""" 'UA-26668199-1']);""")
		self.pylToHtmlResult+=str("""
	  _gaq.push(['_trackPageview']);""")
		self.pylToHtmlResult+=str("""
	
	  (function()""")
		self.pylToHtmlResult+=str(""" {""")
		self.pylToHtmlResult+=str("""
	    var""")
		self.pylToHtmlResult+=str(""" ga""")
		self.pylToHtmlResult+=str(""" =""")
		self.pylToHtmlResult+=str(""" document.createElement('script');""")
		self.pylToHtmlResult+=str(""" ga.type""")
		self.pylToHtmlResult+=str(""" =""")
		self.pylToHtmlResult+=str(""" 'text/javascript';""")
		self.pylToHtmlResult+=str(""" ga.async""")
		self.pylToHtmlResult+=str(""" =""")
		self.pylToHtmlResult+=str(""" true;""")
		self.pylToHtmlResult+=str("""
	    ga.src""")
		self.pylToHtmlResult+=str(""" =""")
		self.pylToHtmlResult+=str(""" ('https:'""")
		self.pylToHtmlResult+=str(""" ==""")
		self.pylToHtmlResult+=str(""" document.location.protocol""")
		self.pylToHtmlResult+=str(""" ?""")
		self.pylToHtmlResult+=str(""" 'https://ssl'""")
		self.pylToHtmlResult+=str(""" :""")
		self.pylToHtmlResult+=str(""" 'http://www')""")
		self.pylToHtmlResult+=str(""" +""")
		self.pylToHtmlResult+=str(""" '.google-analytics.com/ga.js';""")
		self.pylToHtmlResult+=str("""
	    var""")
		self.pylToHtmlResult+=str(""" s""")
		self.pylToHtmlResult+=str(""" =""")
		self.pylToHtmlResult+=str(""" document.getElementsByTagName('script')[0];""")
		self.pylToHtmlResult+=str(""" s.parentNode.insertBefore(ga,""")
		self.pylToHtmlResult+=str(""" s);""")
		self.pylToHtmlResult+=str("""
	  })();""")
		self.pylToHtmlResult+=str("""
	
	</script>""")
		self.pylToHtmlResult+=str("""
	
	</head>""")
		self.pylToHtmlResult+=str("""
<body>""")
		self.pylToHtmlResult+=str("""
	
	<div data-role="page" class="type-interior">""")
		self.pylToHtmlResult+=str("""

		<div data-role="header" data-theme="b">""")
		self.pylToHtmlResult+=str("""
		<h1>""")
		self.pylToHtmlResult+=str("""Pylatte""")
		self.pylToHtmlResult+=str(""" Official""")
		self.pylToHtmlResult+=str(""" Webpage""")
		self.pylToHtmlResult+=str("""</h1>""")
		self.pylToHtmlResult+=str("""
		<a href="../../" target="_self" data-icon="home" data-iconpos="notext" data-direction="reverse" class="ui-btn-right jqm-home">""")
		self.pylToHtmlResult+=str("""Home""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""
	</div>""")
		self.pylToHtmlResult+=str("""<!-- /header -->""")
		self.pylToHtmlResult+=str("""

	<div data-role="content">""")
		self.pylToHtmlResult+=str("""
			<div class="content-primary">""")
		self.pylToHtmlResult+=str("""
			<h1>""")
		self.pylToHtmlResult+=str("""Demo3""")
		self.pylToHtmlResult+=str("""</h1>""")
		self.pylToHtmlResult+=str("""
			<h2>""")
		self.pylToHtmlResult+=str("""SQL""")
		self.pylToHtmlResult+=str(""" Test""")
		self.pylToHtmlResult+=str("""</h2>""")

		import Pylatte.Database.DBMappingParser as pyLatteDBMappingParser

		contact = pyLatteDBMappingParser.pyLatteDBMappingParser()
		result = contact.queryForList("demo.select")
		self.pylToHtmlResult+=str("""
<form id="fileForm" data-ajax="false" class="ui-body ui-body-a ui-corner-all" method="post" action="/sql">""")
		self.pylToHtmlResult+=str("""
<fieldset data-role="controlgroup">""")
		self.pylToHtmlResult+=str("""
	<legend>""")
		self.pylToHtmlResult+=str("""select""")
		self.pylToHtmlResult+=str(""" *""")
		self.pylToHtmlResult+=str(""" from""")
		self.pylToHtmlResult+=str(""" test""")
		self.pylToHtmlResult+=str("""</legend>""")

		for item in result:
			self.pylToHtmlResult+=str("""
<i""")
			self.pylToHtmlResult+=str("""nput""")
			self.pylToHtmlResult+=str(""" type='radio'""")
			self.pylToHtmlResult+=str(""" name='uid'""")
			self.pylToHtmlResult+=str(""" id='radio-choice-""")
			self.pylToHtmlResult+=str(item["uid"])
			self.pylToHtmlResult+=str("""'""")
			self.pylToHtmlResult+=str(""" value='""")
			self.pylToHtmlResult+=str(item["uid"])
			self.pylToHtmlResult+=str("""' />""")
			self.pylToHtmlResult+=str("""
<l""")
			self.pylToHtmlResult+=str("""abel""")
			self.pylToHtmlResult+=str(""" for='radio-choice-""")
			self.pylToHtmlResult+=str(item["uid"])
			self.pylToHtmlResult+=str("""'>""")
			self.pylToHtmlResult+=str(item["uid"])
			self.pylToHtmlResult+=str(""" :""")
			self.pylToHtmlResult+=str( item["name"])
			self.pylToHtmlResult+=str("""</label>""")

			pass
		self.pylToHtmlResult+=str("""
</fieldset>""")
		self.pylToHtmlResult+=str("""

<div data-role="fieldcontain">""")
		self.pylToHtmlResult+=str("""
    <label for="name">""")
		self.pylToHtmlResult+=str("""name:""")
		self.pylToHtmlResult+=str("""</label>""")
		self.pylToHtmlResult+=str("""
    <input type="text" name="name" id="name" value=""  />""")
		self.pylToHtmlResult+=str("""
</div>""")
		self.pylToHtmlResult+=str("""
<label for="select-choice-min" class="select">""")
		self.pylToHtmlResult+=str("""Shipping""")
		self.pylToHtmlResult+=str(""" method:""")
		self.pylToHtmlResult+=str("""</label>""")
		self.pylToHtmlResult+=str("""
<select name="method" id="select-choice-min" data-mini="true">""")
		self.pylToHtmlResult+=str("""
   <option value="insert">""")
		self.pylToHtmlResult+=str("""insert""")
		self.pylToHtmlResult+=str("""</option>""")
		self.pylToHtmlResult+=str("""
   <option value="update">""")
		self.pylToHtmlResult+=str("""update""")
		self.pylToHtmlResult+=str("""</option>""")
		self.pylToHtmlResult+=str("""
   <option value="delete">""")
		self.pylToHtmlResult+=str("""delete""")
		self.pylToHtmlResult+=str("""</option>""")
		self.pylToHtmlResult+=str("""
</select>""")
		self.pylToHtmlResult+=str(""" 
<button type="submit" data-theme="b" name="submit" value="submit-value">""")
		self.pylToHtmlResult+=str("""Submit""")
		self.pylToHtmlResult+=str("""</button>""")
		self.pylToHtmlResult+=str("""
</from>""")
		self.pylToHtmlResult+=str("""
			
			</div>""")
		self.pylToHtmlResult+=str("""<!--/content-primary -->""")
		self.pylToHtmlResult+=str("""

			<div class="content-secondary">""")
		self.pylToHtmlResult+=str("""

				<div data-role="collapsible" data-collapsed="true" data-theme="b" data-content-theme="d">""")
		self.pylToHtmlResult+=str("""

						<h3>""")
		self.pylToHtmlResult+=str("""More""")
		self.pylToHtmlResult+=str(""" in""")
		self.pylToHtmlResult+=str(""" this""")
		self.pylToHtmlResult+=str(""" section""")
		self.pylToHtmlResult+=str("""</h3>""")
		self.pylToHtmlResult+=str("""

						<ul data-role="listview" data-theme="c" data-dividertheme="d">""")
		self.pylToHtmlResult+=str("""
							<li data-role="list-divider">""")
		self.pylToHtmlResult+=str("""Menu""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../index">""")
		self.pylToHtmlResult+=str("""About""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../download">""")
		self.pylToHtmlResult+=str("""Download""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../install">""")
		self.pylToHtmlResult+=str("""Install""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../tutorial">""")
		self.pylToHtmlResult+=str("""Tutorial""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../documentation">""")
		self.pylToHtmlResult+=str("""Documentation""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../faq">""")
		self.pylToHtmlResult+=str("""F""")
		self.pylToHtmlResult+=str(""" A""")
		self.pylToHtmlResult+=str(""" Q""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../contactus">""")
		self.pylToHtmlResult+=str("""Contact""")
		self.pylToHtmlResult+=str(""" us""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../demo1">""")
		self.pylToHtmlResult+=str("""Demo1""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li>""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../demo2">""")
		self.pylToHtmlResult+=str("""Demo2""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<li data-theme="b">""")
		self.pylToHtmlResult+=str("""<a target="_self" href="../demo3">""")
		self.pylToHtmlResult+=str("""Demo3""")
		self.pylToHtmlResult+=str("""</a>""")
		self.pylToHtmlResult+=str("""</li>""")
		self.pylToHtmlResult+=str("""
							<img src="../pyl/image/pylatte.png">""")
		self.pylToHtmlResult+=str("""</img>""")
		self.pylToHtmlResult+=str("""
						</ul>""")
		self.pylToHtmlResult+=str("""
				</div>""")
		self.pylToHtmlResult+=str("""
			</div>""")
		self.pylToHtmlResult+=str("""

		</div>""")
		self.pylToHtmlResult+=str("""<!-- /content -->""")
		self.pylToHtmlResult+=str("""

		<div data-role="footer" class="footer-docs" data-theme="b">""")
		self.pylToHtmlResult+=str("""
				<h4>""")
		self.pylToHtmlResult+=str("""&copy;""")
		self.pylToHtmlResult+=str(""" 2011""")
		self.pylToHtmlResult+=str(""" The""")
		self.pylToHtmlResult+=str(""" Pylatte""")
		self.pylToHtmlResult+=str(""" Project""")
		self.pylToHtmlResult+=str("""</h4>""")
		self.pylToHtmlResult+=str("""
		</div>""")
		self.pylToHtmlResult+=str("""

		</div>""")
		self.pylToHtmlResult+=str("""<!-- /page -->""")
		self.pylToHtmlResult+=str("""

	</body>""")
		self.pylToHtmlResult+=str("""
</html>""")
		self.sessionDic=session
		pass
	def getHtml(self):
		return self.pylToHtmlResult
		pass
	def getSession(self):
		return self.sessionDic
		pass
