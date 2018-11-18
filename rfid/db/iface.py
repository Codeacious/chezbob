from pg import DB

class RFIDIface:

    def __init__(self):
        self.db = DB(dbname='chezbob_rfid', host='localhost', port=5432, user='postgres', passwd='toor')

    def setup(self):
        self.db.query(("CREATE TABLE IF NOT EXISTS"
                       "rfid_tags(tag_id character(30) NOT NULL,"
                       "last_seen_unix_secs timestamp DEFAULT current_timestamp,"
                       "item_id integer NOT NULL"
                       "CONSTRAINT rfid_tags_pkey PRIMARY KEY (tag_id)),"
                       "CONSTRAINT fk_item_id FOREIGN KEY (item_id) references tagged_items(item_id)"))
        self.db.query('CREATE TABLE IF NOT EXISTS tagged_items(item_id SERIAL NOT NULL,item_name text NOT NULL,item_description text,item_upc character varying(30),tag_id character(30),CONSTRAINT tagged_items_pkey PRIMARY KEY (item_id))')

    def addItem(self, name, description, upc,tagId):
        self.db.insert('tagged_items', item_name=name, item_description=description, item_upc=upc, tag_id=tagId)

    def justSeen(self, taglist):
        for tag in taglist:
            self.db.query("INSERT INTO rfid_tags (tag_id,last_seen_unix_secs) VALUES ('%s',now()) ON CONFLICT (tag_id) DO UPDATE SET last_seen_unix_secs=now()" % tag)

    def getLastSeen(self, itemId):
        result = self.db.query('SELECT last_seen_unix_secs FROM rfid_tags WHERE tag_id=(SELECT tag_id FROM tagged_items WHERE item_id=%d)' % itemId)
        result = result.getresult()
        return result[0][0] if len(result) > 0 else None

# TESTING
client = RFIDIface()
client.setup()
client.addItem('something', 'in chezbob', '12345678', 'a')
client.justSeen(['a','b','c','d'])
last = client.getLastSeen(1)
print(last)