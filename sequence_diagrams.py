import sublime, sublime_plugin, os, urllib.parse, urllib.request, re, hashlib, shelve, time

class WebSequenceDiagramPlugin(sublime_plugin.EventListener):
	def __init__(self):
		self.settings = None

	def set_server(self, text):
		self.settings.set("sequence_server", text)
		self.settings = None

	def on_post_save(self, view):
		start = time.time()

		if not view.file_name().endswith(".seq"):
			return
		if not view.settings().get("sequence_server"):
			self.settings = view.settings()
			view.window().show_input_panel("Sequence Diagram Server/Port?", "", self.set_server, None, None)
			return

		print("{}: {}: {}".format("Settings Check", time.time(), (time.time() - start)))

		print(view.file_name() + ".sums")
		sums = shelve.open(view.file_name() + ".sums")

		print("{}: {}: {}".format("Shelf Pulled", time.time(), (time.time() - start)))

		filename = None
		contents = ""
		with open(view.file_name(), "r") as ins:
			for line in ins:
				if line.startswith(":"):
					print("{}: {}: {}".format("Loop", time.time(), (time.time() - start)))
					if filename:
						self.fetch_if(contents, filename, view.settings().get("sequence_server"), sums)
					filename = os.path.join(os.path.dirname(view.file_name()), line[1:].strip() + ".png")
					contents = ""
					continue
				contents += line

			self.fetch_if(contents, filename, view.settings().get("sequence_server"), sums)

			print("{}: {}: {}".format("Done Loop", time.time(), (time.time() - start)))
			sums.close()


		print("{}: {}: {}".format("Sums Written", time.time(), (time.time() - start)))

	def fetch_if(self, text, filename, server, sums):
		m = hashlib.md5()
		m.update(text.encode('utf-8'))
		md5 = m.hexdigest()

		if (filename not in sums) or md5 != sums[filename]:
			self.fetch_diagram(
				server,
				text,
				filename)
		else:
			print("Skipping " + filename)

		sums[filename] = md5

	def fetch_diagram(self, server, text, outputFile, style = 'vs2010' ):
		start = time.time()
		print("Generating " + outputFile + " From " + server)
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

		print("{}: {}: {}".format("Fetch", time.time(), (time.time() - start)))
		return True