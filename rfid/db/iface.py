from pg import DB

class RFIDIface:

	def __init__(self):
		self.db = DB(dbname='chezbob_rfid', host='localhost', port=5432, user='postgres', passwd='toor')

	def setup(self):
		self.db.query('CREATE TABLE IF NOT EXISTS rfid_tags(tag_id character(30) NOT NULL,last_seen_unix_secs timestamp DEFAULT current_timestamp,CONSTRAINT rfid_tags_pkey PRIMARY KEY (tag_id))')

	def justSeen(self, taglist):
		for tag in taglist:
			self.db.query("INSERT INTO rfid_tags (tag_id,last_seen_unix_secs) VALUES ('%s',now()) ON CONFLICT (tag_id) DO UPDATE SET last_seen_unix_secs=now()" % tag)

# TESTING
client = RFIDIface()
client.setup()
client.justSeen(['a','b','c','d'])