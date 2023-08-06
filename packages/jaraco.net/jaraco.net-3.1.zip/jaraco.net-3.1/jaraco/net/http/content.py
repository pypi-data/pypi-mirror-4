import cherrypy

form = """
<form method="post" enctype="multipart/form-data">
	<input type="file" name="file"/>
	<input type="submit" />
</form>
"""
class ContentTypeReporter(object):
	@cherrypy.expose
	def index(self, file=None):
		if not file:
			return form
		return "Content type is {file.content_type}".format(**vars())

	@classmethod
	def run(cls):
		config = {
			'global': {
				'server.socket_port': 8080,
				'server.socket_host': '::0',
			},
		}
		cherrypy.quickstart(cls(), config=config)
