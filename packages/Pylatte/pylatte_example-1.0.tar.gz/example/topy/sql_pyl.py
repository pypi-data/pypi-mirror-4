# -*- coding: utf-8 -*- 
import pylatte.web.formFile as formFile
class sql:
	pylToHtmlResult=""
	sessionDic=dict()
	def __init__(self,param,pyFile,session,headerInfo,lattedb):
		self.generate(param,pyFile,session,headerInfo,lattedb)

	def generate(self,param,pyFile,session,headerInfo,lattedb):

		import pylatte.database.DBMappingParser as pyLatteDBMappingParser
		test = pyLatteDBMappingParser.pyLatteDBMappingParser()

		if param=={} :
			pass
		elif param['method']=="insert":
			value = dict();
			value["name"]= param['name'];
			test.queryForList("demo.insert",value)
			pass
		elif param['method']=="update":
			value = dict();
			value["uid"]= param['uid'];
			value["name"]= param['name'];
			test.queryForList("demo.update",value)
			pass
		elif param['method']=="delete":
			value = dict();
			value["uid"]= param['uid'];
			test.queryForList("demo.delete",value)
			pass
		self.pylToHtmlResult+=str("""<script type="text/javascript">
	alert("sql suecess!!");
	location.href='/demo3';
</script>""")
		self.sessionDic=session
		pass
	def getHtml(self):
		return self.pylToHtmlResult
		pass
	def getSession(self):
		return self.sessionDic
		pass
