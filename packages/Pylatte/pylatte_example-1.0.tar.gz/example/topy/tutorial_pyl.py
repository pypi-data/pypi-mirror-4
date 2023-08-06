# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class tutorial:
	pylToHtmlResult=""
	sessionDic=dict()
	def __init__(self,param,pyFile,session,headerInfo,lattedb):
		self.generate(param,pyFile,session,headerInfo,lattedb)

	def generate(self,param,pyFile,session,headerInfo,lattedb):
		self.pylToHtmlResult+=str("""<!DOCTYPE html>
<html>
	<head>
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
	<title>Pylatte - Web framework based on Python3</title>
	
	<!-- favicon -->
	<link rel="shortcut icon" href="../pyl/favicon.ico" type="image/x-icon">
	<link rel="icon" href="../pyl/favicon.ico" type="image/x-icon">

	<!-- Include required JS files -->
	<script type="text/javascript" src="../pyl/syntaxhighlighter/js/xregexp.js"></script>
	<script type="text/javascript" src="../pyl/syntaxhighlighter/js/shCore.js"></script>
	 
	<!--
	    At least one brush, here we choose JS. You need to include a brush for every
	    language you want to highlight
	-->
	<script type="text/javascript" src="../pyl/syntaxhighlighter/lang/shBrushXml.js"></script>
	<script type="text/javascript" src="../pyl/syntaxhighlighter/lang/shBrushBash.js"></script>
	 
	<!-- Include *at least* the core style and default theme -->
	<link href="../pyl/syntaxhighlighter/css/shCore.css" rel="stylesheet" type="text/css" />
	<link href="../pyl/syntaxhighlighter/css/shThemeDefault.css" rel="stylesheet" type="text/css" />
	
	
	
	<link rel="stylesheet"  href="../pyl/css/jquery.mobile-1.2.0.css"/>
	<link rel="stylesheet"  href="../pyl/css/jqm-docs.css"/>
	
	<script src="../pyl/js/jquery.js"></script>
	<script src="../pyl/js/jqm-docs.js"></script>
	<script src="../pyl/js/jquery.mobile.themeswitcher.js"></script>
	<script src="../pyl/js/jquery.mobile-1.2.0.min.js"></script>
	
	<script type="text/javascript">

	  var _gaq = _gaq || [];
	  _gaq.push(['_setAccount', 'UA-26668199-1']);
	  _gaq.push(['_trackPageview']);
	
	  (function() """)
		self.pylToHtmlResult+=str("""	    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	  })();
	
	</script>
	
	</head>

<body>
	<div data-role="page" class="type-interior">

		<div data-role="header" data-theme="b">
		<h1>Pylatte Official Webpage</h1>
		<a href="../../" target="_self" data-icon="home" data-iconpos="notext" data-direction="reverse" class="ui-btn-right jqm-home">Home</a>
	</div><!-- /header -->

	<div data-role="content">
			<div class="content-primary">
			<h1>Tutorial</h1>
				
			<h2>Hello Pylatte</h2>
				<p>Let's print <i>Hello Pylatte</i>on pylatte tutorial as a first step. First of all, open a text editor, and it will be saved as <i>hellopy.<b>pyl</b></i></p>
				<p>You can use python code in pyl file format on pylatte. pyl consists of HTML and python.</p>
				<p>To make pyl page working on pylatte, wrap python code with <b>&lt;""")
		self.pylToHtmlResult+=str("""</b> and <b>""")
		self.pylToHtmlResult+=str("""&gt;</b>. And if you put your <i>variable</i> between <b>&lt;""")
		self.pylToHtmlResult+=str("""=</b> and <b>""")
		self.pylToHtmlResult+=str("""&gt;</b> such as <b>&lt;""")
		self.pylToHtmlResult+=str("""=</b><i>variable</i><b>""")
		self.pylToHtmlResult+=str("""&gt;</b>, the <i>variable</i> will be automatically printed on the web page by pylatte translation module. </p>
				<p>Caution : If you use <b>print()</b> function, it will be printed on web server console.</p>
			
				<pre class="brush: xml">
				&#123;&#36;
				hi=&quot;hello pylatte&quot;
				&#36;&#125;
				<h1>&#123;&#36;=hi&#36;&#125;</h1>
				</pre>
				<p>In python language, indentation is absolutely important. So we strongly recommend to use python code under <b>&lt;""")
		self.pylToHtmlResult+=str("""</b>, and type <b>""")
		self.pylToHtmlResult+=str("""&gt;</b> on new line after python code. Refer to the following code.</p>
				<p>Type the code in hellopy.pyl and save it again. After running pylatte web server, you can see <b>hello pylatte</b>.
			
			<h2>Starting pylatte web server</h2>
				<p>Basically, default port number is 80 on HTTP. If you want, you can change port number in <i>pylatte_config.xml</i></p>
				<pre class="brush: xml">
					<pylatte-server>
						<port>80</port>
					</pylatte-server>
				</pre>
				<p>There are many options in <i>pylatte_config.xml</i>. To change port number, we need to focus on only &lt;pylatte-server&gt; tag. Modify the value of &lt;port&gt; tag from default port(80) to what you want(e.g. 8000).</p>
				<p>Caution : You have to check if the port number is being used by another program before you change.</p>
				
				<p>To start pylatte web server, move to appropriate path where pylatte is installed and run following command into terminal. If operating system is Windows, just execute the latteServerStart.py file.</p>
				<pre class="brush: bash">
					sudo python3 latteServerStart.py
				</pre>
				<p>There are just one more step to see <b>hello pylatte</b>. Take URL Mapping below.</p>
				
			<h2>URL Mapping</h2>
				<p>To make pylatte security safe, it is neccesary to fix &lt;pylatte&gt; and &lt;pylatte-mapping&gt; tag in <i>pylatte_config.xml</i></p>
				<pre class="brush: xml">
					<pylatte>
						<pylatte-name>hello_pylatte</pylatte-name>
						<pylatte-pyl>hellopy.pyl</pylatte-pyl>
					</pylatte>
					<pylatte-mapping>
						<pylatte-name>hello_pylatte</pylatte-name>
						<url-mapping>/py</url-mapping>
					</pylatte-mapping>	
				</pre>
				<p>&lt;pylatte-name&gt; value(e.g. hello_pylatte) in &lt;pylatte&gt; and &lt;pylatte-mapping&gt; is just name to identify each mapping information.</p>
				<p>&lt;pylatte-pyl&gt; value(e.g. hellopy.pyl) in &lt;pylatte&gt; is real pyl page we make. it will be accessed by &lt;url-mapping&gt; value in &lt;pylatte-mapping&gt;. Once more, you have to access http://localhost/py, NOT to http://localhost/hellopy.pyl. This can hide original url, so we think it would make pylatte securtiy much higher.</p>
				<p>Congratulation, now you can access to <a href="http://localhost/py">http://localhost/py</a> instead of http://localhost/hellopy.pyl to see hello pylatte.</p>
				
			<h2>Filter</h2>
				<p>Sometimes, we need to process one same function in many pages before the pages get started. Filter module on Pylatte perfectly supports this.</p>
				<p>It can be configured in <i>pylatte_config.xml</i>.</p>
				<pre class="brush: xml">
					<filter>
						<filter-name>testFilter</filter-name>
						<filter-pyl>filter/filter.pyl</filter-pyl>
					</filter>
					<filter-mapping>
						<filter-name>testFilter</filter-name>
						<filter-url>hellopy.pyl</filter-url>
						<filter-url>byepy.pyl</filter-url>
					</filter-mapping>
				</pre>
				<p>Look at this xml code. &lt;filter-name&gt; value(e.g. testFilter) in &lt;filter&gt; and &lt;filter-mapping&gt; is just name to identify each filter information.</p>
				<p>&lt;filter-pyl&gt; value will be executed at first when you access to &lt;filter-url&gt; values.</p>
				<p>For instance, filter/filter.pyl will be executed at first when you access to byepy.pyl or hellopy.pyl in the code.</p>
				<p>So you don't need to add same code to many pages which require same function anymore.</p>
				
			<h2>GET & POST</h2>
				<p>There are two kinds of method to deal with GET & POST parameter.</p>
				<p>When you request some parameter values using GET method or POST method, you can get the parameter values as following.</p>
				<pre class="brush: xml">
					&#123;&#36;=param&#36;&#125;
				</pre>
				<p>The variable <b>param</b> has all requested values as dictionary type like <i>""")
		self.pylToHtmlResult+=str(""""id":pylatte, "password":python}</i>. Definately, you can get specific value such as following.</p> 
				<pre class="brush: xml">
					&#123;&#36;=param[&quot;id&quot;]&#36;&#125;
				</pre>
				<p>Pylatte does not support the other methods like PUT, DELETE.</p>
				
			<h2>Session</h2>
				<p>Pylatte supports sesson management allocating session datas for each accessor.</p>
				<p>This session data type is dictionary. The way to use is similar with GET & POST above. Refer to following code.</p>
				<pre class="brush: xml">
					session[&quot;name&quot;] = &quot;pylatte&quot;
					session[&quot;age&quot;] = 1
				</pre>	
				<p>Pylatte manages session data through session module. Usually, it is required to use in membership page to deal with each member's session data. </p>

			<h2>File Upload</h2>
				<p>You can implement file upload function with a file upload module on Pylatte. When you use &lt;form&gt; tag, it is compulsory to put attribute : <b>enctype="multipart/form-data</b> into the tag.</p>
				<pre class="brush: xml">
				
					<form  method="post" enctype="multipart/form-data" action="http:/localhost/pageToProcessPost">
						<input type="file" name="filepy" />
						<input type="sudmit" value="click" />
					</form>
				</pre>
				<p>Now you can upload a file as post parameters in pageToProcessPost(This is a mapped page name by mapping module at <i>pylatte_config.xml</i>) page. Refer to following code.</p>
				<pre class="brush: xml">
					&#123;&#36;
					pyformFile=formFile.formFile(pyFile)
					pyformFile.moveUploadFile(&quot;filepy&quot;,&quot;download&quot;,&quot;pylatte.jpg&quot;)
					&#36;&#125;
				</pre>
				<p>you can receive the file information to variable with using <b>formFile.formFile(pyFile)</b>. And execute moveUploadFile mothod from the variable to complete upload file to server. Parameters of moveUploadFile are name, folder name, and file name in order.</p> 
				<p>In addition, pyFile[<i>name</i>]</p> has a little information about the file as dictionary type.
			
			<h2>Database</h2>
				<p>First of all, to set your database, it is needed to fix &lt;sql&gt; values in <i>db_mapping.xml</i> about MySQL connection information.</p>
				<pre class="brush: xml">
					<sql db="mysql">
						<host>localhost</host>
						<user>user</user>
						<password>password</password>
						<dbName>pylatte</dbName>
					</sql>
				</pre>
				<p>Only MySQL is an available database on Pylatte now. In &lt;sql&gt;, it is required to fill with host, user, password, database name.</p>
				
				<h3>Simple way to use database</h3>				
				<p><b>latteDatabase()</b> has to be written on the code specifically before using database. After that, execute SQL what you need through <b>latteDB.query()</b> method. And then, use <b>latteDB.store_result()</b> method which return result of processing the SQL.</p>
				<p>The result include not only result of SQL but also some methods. To see how to use a database, check example code below.</p>
				<pre class="brush: xml">
					&#123;&#36;
					latteDatabase()					
					latteDB.query(&quot;select * from test&quot;)
					result=latteDB.store_result()
					&#36;&#125;
					&lt;div id="dbdiv"&gt;
					&#123;&#36;=result.fetch_row()&#36;&#125;
					&lt;/div&gt;
				</pre>
				<p>This code returns tuple type result by fetch_row()</p>
				<p><b>fetch_row()</b> method takes some additional parameters. </p>
				<p>The first one is, how many rows (maxrows) should be returned. By default, it returns one row. It may return fewer rows than you asked for, but never more. If you set maxrows=0, it returns all rows of the result set. If you ever get an empty tuple back, you ran out of rows.</p>
				<pt>The second parameter (how) tells it how the row should be represented. By default, it is zero which means, return as a tuple. how=1 means, return it as a dictionary, where the keys are the column names, or table.column if there are two columns with the same name (say, from a join). how=2 means the same as how=1 except that the keys are always table.column.</p>
				
				<h3>Advanced way to use database</h3>
				<p><b>latteDatabaseExt()</b> has to be written on the code specifically before using database. 
				<p>In this case, DBMappingParser class and db_mapping.xml file are required to use. Refer to following code.</p>
				<pre class="brush: xml">
					<sqlMap id="user">
						<select id="select1">SELECT * FROM table</select>
						<select id="select2">SELECT * FROM table WHERE age = """)
		self.pylToHtmlResult+=str("""age""")
		self.pylToHtmlResult+=str("""</select>
						<insert id="insert1">INSERT INTO table VALUES (""")
		self.pylToHtmlResult+=str("""name""")
		self.pylToHtmlResult+=str(""", """)
		self.pylToHtmlResult+=str("""age""")
		self.pylToHtmlResult+=str(""")</insert>
						<update id="update1">UPDATE table SET age = """)
		self.pylToHtmlResult+=str("""age""")
		self.pylToHtmlResult+=str(""" WHERE name = """)
		self.pylToHtmlResult+=str("""name""")
		self.pylToHtmlResult+=str("""</update>
						<delete id="delete1">DELETE FROM table WHERE age = """)
		self.pylToHtmlResult+=str("""age""")
		self.pylToHtmlResult+=str("""</delete>
					</sqlMap>
				</pre>
				<p>This is xml code in <i>db_mapping.xml file</i>. &lt;sqlMap&gt; tag needs attribute 'id'. And its child nodes (e.g. select, insert, update, delete ...) also need attribute 'id'. These 'id' are used to call SQL which is values of the childe nodes. Let's see how to deal with database using these SQLs.</p>
				<pre class="brush: xml">
					&#123;&#36;
					latteDatabaseExt()
				
					db = DBMappingParser.pyLatteDBMappingParser()
					parameter = """)
		self.pylToHtmlResult+=str("""&quot;age&quot;:1, &quot;name&quot;:&quot;pylatte&quot;}
					
					result1 = db.queryForList(&quot;user.select1&quot;)	
					result2 = db.queryForList(&quot;user.select2&quot;, parameter)
					&#36;&#125;
				</pre>
				<p>First of all, declare on variable and call DBMappingParser.pyLatteDBMappingParser() to save database object to the variable.</p>
				<p>Secondly, define dictionary type parameter. This will be replaced matched value in SQL.</p>
				<p>At last, call queryForList() method via the variable declared on first step.</p>
				<p>queryForList() method takes two parameters.</p>
				<p>First one indicates specific SQL in db_mapping.xml by id. For example, 'user.select1' indicates a value in specific tag which has id 'select1' in &lt;sqlMap&gt; tag having id 'user'. So 'user.select1' get replaced to &quot;SELECT * FROM test&quot;</p>
				<p>Second parameter is optional. When SQL indicated by first parameter includes variable """)
		self.pylToHtmlResult+=str("""keys""")
		self.pylToHtmlResult+=str(""", this is mandatory. As you see above example code, second parameter is dictionary type. In the parameter, the each values automatically gets replaced with each matched """)
		self.pylToHtmlResult+=str("""keys""")
		self.pylToHtmlResult+=str(""" in SQL. So select2 will be traslated from <b>SELECT * FROM test WHERE age = """)
		self.pylToHtmlResult+=str("""age""")
		self.pylToHtmlResult+=str("""</b> to <b>SELECT * FROM test WHERE age = 1</b></p>
				<p>queryForList() method returns tuple type as a result.</p>
				
							
			<h2>Server Information</h2>
				<p>It is possible to get HTTP header information that you required to Pylatte web server. It is also saved as dictionary type. Refer to following code to see how to use it in pyl.</p>
				<pre class="brush: xml">
					&#123;&#36;=headerInfo["User-Agent"]&#36;&#125;
					&#123;&#36;=headerInfo["Accept-Encoding"]&#36;&#125;
				</pre>
				<p>There are planty of header information. Pylatte support most common header information.</p>
			</div><!--/content-primary -->

			<div class="content-secondary">

				<div data-role="collapsible" data-collapsed="true" data-theme="b" data-content-theme="d">

						<h3>More in this section</h3>

						<ul data-role="listview" data-theme="c" data-dividertheme="d">
							<li data-role="list-divider">Menu</li>
							<li><a target="_self" href="../index">About</a></li>
							<li><a target="_self" href="../download">Download</a></li>
							<li><a target="_self" href="../install">Install</a></li>
							<li data-theme="b"><a target="_self" href="../tutorial">Tutorial</a></li>
							<li><a target="_self" href="../documentation">Documentation</a></li>
							<li><a target="_self" href="../faq">F A Q</a></li>
							<li><a target="_self" href="../contactus">Contact us</a></li>
							<li><a target="_self" href="../demo1">Demo1</a></li>
							<li><a target="_self" href="../demo2">Demo2</a></li>
							<li><a target="_self" href="../demo3">Demo3</a></li>
							<img src="../pyl/image/pylatte.png"></img>
						</ul>
				</div>
			</div>

		</div><!-- /content -->

		<div data-role="footer" class="footer-docs" data-theme="b">
				<h4>&copy; 2011 The Pylatte Project</h4>
		</div>

		</div><!-- /page -->
	
		</body>
	<!-- Finally, to actually run the highlighter, you need to include this JS on your page -->
	<script type="text/javascript">
		SyntaxHighlighter.all()
	</script>
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
