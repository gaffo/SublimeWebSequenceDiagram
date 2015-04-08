import sublime, sublime_plugin

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
		print(view.settings().get("sequence_server"))
