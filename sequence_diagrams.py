import sublime, sublime_plugin, os, urllib.parse, urllib.request, re

class WebSequenceDiagramPlugin(sublime_plugin.EventListener):
	def __init__(self):
		self.settings = None

	def set_server(self, text):
		self.settings.set("sequence_server", text)
		self.settings = None

	def on_post_save(self, view):
		if not view.file_name().endswith(".seq"):
			return
		if not view.settings().get("sequence_server"):
			self.settings = view.settings()
			view.window().show_input_panel("Sequence Diagram Server/Port?", "", self.set_server, None, None)
			return

		print("saving sequence")

		filename = None
		contents = ""
		with open(view.file_name(), "r") as ins:
			for line in ins:
				if line.startswith(":"):
					if filename:
						self.fetch_diagram(
							view.settings().get("sequence_server"),
							contents,
							filename)
					filename = os.path.join(os.path.dirname(view.file_name()), line[1:].strip() + ".png")
					contents = ""
					continue
				contents += line



	def fetch_diagram(self, server, text, outputFile, style = 'vs2010' ):
		request = {}
		request["message"] = text
		request["style"] = style
		request["apiVersion"] = "1"

		url = urllib.parse.urlencode(request)

		f = urllib.request.urlopen("http://" + server + "/", str.encode(url))
		line = f.readline().decode("utf-8")
		f.close()

		expr = re.compile("(\?(img|pdf|svg|png)=[a-zA-Z0-9]+)")
		m = expr.search(line)

		if m == None:
			print("Invalid response from server.")
			return False

		urllib.request.urlretrieve("http://" + server + "/" + m.group(0),
				outputFile )
		return True