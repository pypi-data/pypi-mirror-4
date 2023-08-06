# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class documentation:
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
				<h1>Documentation</h1>
				<div data-role="collapsible-set" data-theme="c" data-content-theme="d">
				<div data-role="listview" data-inset="true" data-filter="true" data-filter-theme="c">
					<div data-role="collapsible" data-collapsed="true">
						<h3>pylatte_config.xml</h3>
						<p>Configuration about Server port number, URL Mapping, and Filter</p>
						<pre class="brush: xml">
							<config>
								<pylatte-server>
									<port>80</port>	<!-- Pylatte web server port number. 80 set by default -->
								</pylatte-server>
							
								<latteUrl><!-- URL Mapping pairs -->
									<!-- From hostname/pylatte to hostname/sample.pyl -->
									<!-- pylatte-name is a just name of each pair. -->
									<pylatte>
										<pylatte-name>mapping_test</pylatte-name>
										<pylatte-pyl>sample.pyl</pylatte-pyl>
									</pylatte>
									<pylatte-mapping>
										<pylatte-name>mapping_test</pylatte-name>
										<url-mapping>/pylatte</url-mapping>
									</pylatte-mapping>	
								</latteUrl>
								
								<latteFilter><!-- Filter pairs -->
									<!-- filter-pyl code are executed first before filter-url pages are accessed -->
									<!-- filter-name is a just name of each pair. -->
									<filter>
										<filter-name>filter_test</filter-name>
										<filter-pyl>filter/sample_filter.pyl</filter-pyl>
									</filter>
									<filter-mapping>
										<filter-name>filter_test</filter-name>
										<filter-url>documenation.pyl</filter-url>
										<filter-url>tutorial.pyl</filter-url>
										<filter-url>contact.pyl</filter-url>
									</filter-mapping>
								</latteFilter>
							</config>
						</pre>
					</div>
					<div data-role="collapsible"  data-collapsed="true">
						<h3>db_mapping.xml</h3>
						<p>Configuration about database information and using advanced SQL</p>
						<pre class="brush: xml">
							<database>
								<sql db="mysql"><!-- information about MySQL to connect database -->
									<host>localhost</host>
									<user>root</user>
									<password>pylatte</password>
									<dbName>pylatte</dbName>
								</sql>
								
								<sqlmap id="user"><!-- SQL set-->
									<!-- SQL list to use -->
									<!-- """)
		self.pylToHtmlResult+=str("""variable""")
		self.pylToHtmlResult+=str(""" is replaced with python variable -->
								    <seIect id="select1">SELECT * FROM table</select>
								    <seIect id="select2">SELECT * FROM table WHERE age = """)
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
								</sqlmap>
							</database>
						</pre>
					</div>
					<div data-role="collapsible"  data-collapsed="true">
						<h3>latteServerStart.py</h3>
						<p>Turn on Pylatte web server</p>
						<ul>
							<li>parseServerPort()</li>
							<p>Set a server port number by reading pylatte_config.xml</p>
							<li>worker()</li>
							<p>Work a server</p>
							<li>my_service()</li>
							<p>checking a command from interective prompt.</p>
						</ul>
					</div>
					<div data-role="collapsible"  data-collapsed="true">
						<h3>pyLatteConfigParser Class</h3>
						<p>This class is just for a test.</p>
						<ul>
							<li>__init__()</li>
							<p>Set a Mapping information and Filter information by reading pylatte_config.xml</p>
							<li>parserUrlMappingExcute()</li>
							<p>Bring the path to access(execute) pyl file actually from a xml file</p>
							<li>parseUrlMappingUrl()</li>
							<p>Bring the virtual URL to link to one pyl file from a xml file</p>
							<li>makeUrlMap()</li>
							<p>Make dictionay mapping data pairs</p>
							<li>parseFilterPyl()</li>
							<p>Bring the path to filter pyl file actually from a xml file</p>
							<li>parseFilterUrl()</li>
							<p>Bring the path to be filtered pyl files from a xml file</p>
							<li>makeFilterMap()</li>
							<p>Make dictionay filter data pairs</p>
							<li>getUrlMap()</li>
							<p></p>
							<li>getDataBaseInfo()</li>
							<p></p>
							<li>getFilterMap()</li>
							<p></p>
						</ul>
					</div>
					<div data-role="collapsible"  data-collapsed="true">
						<h3>pyLatteDBMappingParser Class</h3>
						<p>To deal with database based on MySQL</p>
						<ul>
							<li>__init__()</li>
							<p>Ready for reading database information</p>
							<li>loadXmlFromFile()</li>
							<p>Load XML document about database information and SQL Mapping information</p>
							<li>parseDataBaseInfo()</li>
							<p>Get database information(host, user, password, database name) from XML document
        And Connect to MySQL to use the database</p>
        					<li>queryProcessing</li>
        					<p>Execute SQL with replacing variables in SQL.</p>
        					<li>queryForList()</li>
        					<p>Looking for matched SQL with specified id from XML document</p>
						</ul>
					</div>
					<div data-role="collapsible"  data-collapsed="true">
						<h3>formFile Class</h3>
						<p>This class is just for a test.</p>
						<ul>
							<li>__init__()</li>
							<p>Initializing variables.</p>
							<li>moveUploadFile()</li>
							<p>Upload files to indicated path.</p>
							<li>getError</li>
							<p>Return an error message.</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>latteServer Class</h3>
						<p>This class is just for a test.</p>
						<ul>
							<li>__init__()</li>
							<p>Read URL mapping and database information</p>
							<li>do_GET()</li>
							<p>GET parameter processing</p>
							<li>do_POST()</li>
							<p>POST parameter processing</p>
							<li>do_HEAD()</li>
							<p>Head in formation processing</p>
							<li>send_head()</li>
							<p>This sends the response code and MIME headers.</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>latteSocketServer Class</h3>
						<p>This class is just for a test.</p>
						<ul>
							<li>__init__()</li>
							<p>Server started entierly.</p>
							<li>server_bind()</li>
							<p>Binding a server</p>
							<li>shutdown()</li>
							<p>Shut down a server</p>
							<li>sessionFileRemove()</li>
							<p>Remove session files generated before</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>methodGetGetParam Class</h3>
						<p>Reading GET parameters</p>
						<ul>
							<li>__init__()</li>
							<p>Parsing GET parameters from accessed URL.</p>
							<li>getParam()</li>
							<p>Return GET parameters as dictionary type.</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>methodGetPostParam Class</h3>
						<p>Reading POST parameters</p>
						<ul>
							<li>__init__()</li>
							<p>Get POST parameters from a loaded page</p>
							<li></li>getParam</li>
							<p>Return POST parameters as dictionary type</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>postMultipartForm Class</h3>
						<p>This class is used to send multipart/form</p>
						<ul>
							<li>__init__()</li>
							<p>Save payload datas in the start</p>
							<li>__splitPayload()</li>
							<p>Split received datas</p>
							<li>__analysisData()</li>
							<p>Analysis splited datas</p>
							<li>__getTmpHashKey()</li>
							<p>Make a temporary file name.</p>
							<li>getFileInfo()</li>
							<p>Return file information.</p>
							<li>getParam()</li>
							<p>Retrun input data except for file information</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>pylToPy Class</h3>
						<p>Translation module from pyl file to py(python) file</p>
						<ul>
							<li>__init__()</li>
							<p>Read a pyl file</p>
							<li>translationPy()</li>
							<p>Translate code from .pyl to .py</p>
							<li>outPy()</li>
							<p>Get original pyl name to save py file.</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>requestHeaderInfo Class</h3>
						<p>Information of request header</p>
						<ul>
							<li>__init__()</li>
							<p>Generate head information from header</p>
							<li>getHeaderInfo()</li>
							<p>Return header information as dictionary type</p>
						</ul>
					</div>
					<div data-role="collapsible" data-collapsed="true">
						<h3>session Class</h3>
						<p>Dealing with session information</p>
						<ul>
							<li>checkAvailableSession()</li>
							<p>Check whether the session is valid or not.</p>
							<li>genSessionKey()</li>
							<p>Generate session file.</p>
							<li>setSessionData()</li>
							<p>Save file using generated key string</p>
							<li>getSessionData()</li>
							<p>Get session data using the session key.</p>
							<li>dictToSessionData()</li>
							<p>Change form from dictionary type to session data type</p>
							<li>sessionDataTodict()</li>
							<p>Change form from session data type to dictionary type</p>
						</ul>
					</div>
				</div>
				</div>
			</div><!--/content-primary -->
	
			<div class="content-secondary">

				<div data-role="collapsible" data-collapsed="true" data-theme="b" data-content-theme="d">

					<h3>More in this section</h3>

					<ul data-role="listview" data-theme="c" data-dividertheme="d">
						<li data-role="list-divider">Menu</li>
						<li><a target="_self" href="../index">About</a></li>
						<li><a target="_self" href="../download">Download</a></li>
						<li><a target="_self" href="../install">Install</a></li>
						<li><a target="_self" href="../tutorial">Tutorial</a></li>
						<li data-theme="b"><a target="_self" href="../documentation">Documentation</a></li>
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
		<!-- Finally, to actually run the highlighter, you need to include this JS on your page -->
		<script type="text/javascript">
		     SyntaxHighlighter.all()
		</script>
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
