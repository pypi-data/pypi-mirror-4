from pymysqlreplication.tests import base
from pymysqlreplication import BinLogStreamReader
from pymysqlreplication.event import *
from pymysqlreplication.constants.BINLOG import *
from pymysqlreplication.row_event import *


class TestBasicBinLogStreamReader(base.PyMySQLReplicationTestCase):
    def test_read_query_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)

        #RotateEvent
        event = self.stream.fetchone()
        self.assertEqual(event.position, 4)
        self.assertEqual(event.next_binlog, "mysql-bin.000001")

        #FormatDescription
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, QueryEvent)
        self.assertEqual(event.query, query)

    def test_reading_rotate_event(self):
        query = "CREATE TABLE test_2 (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)

        rotate_event = self.stream.fetchone()
        self.stream.close()

        query = "CREATE TABLE test_3 (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)

        rotate_event = self.stream.fetchone()

    def test_connection_stream_lost_event(self):
        self.stream.close()
        self.stream = BinLogStreamReader(connection_settings = self.database, blocking = True)

        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)
        query2 = "INSERT INTO test (data) VALUES('a')"
        for i in range(0, 10000):
            self.execute(query2)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()

        #FormatDescription
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, QueryEvent)
        self.assertEqual(event.query, query)

        self.conn_control.kill(self.stream._stream_connection.thread_id())
        for i in range(0, 1000):
            event = self.stream.fetchone()
            self.assertIsNotNone(event)

    def test_filtering_events(self):
        self.stream.close()
        self.stream = BinLogStreamReader(connection_settings = self.database, only_events = [QueryEvent])
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)

        event = self.stream.fetchone()
        self.assertIsInstance(event, QueryEvent)
        self.assertEqual(event.query, query)

    def test_write_row_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('Hello World')"
        self.execute(query)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()
        #FormatDescription
        self.stream.fetchone()
        #QueryEvent for the Create Table
        self.stream.fetchone()

        #QueryEvent for the BEGIN
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, TableMapEvent)

        event = self.stream.fetchone()
        if self.isMySQL56AndMore():
            self.assertEqual(event.event_type, WRITE_ROWS_EVENT)
        else:
            self.assertEqual(event.event_type, WRITE_ROWS_EVENT_V1)
        self.assertIsInstance(event, WriteRowsEvent)
        self.assertEqual(event.rows[0]["values"]["id"], 1)
        self.assertEqual(event.rows[0]["values"]["data"], "Hello World")
        self.assertEqual(event.schema, "pymysqlreplication_test")
        self.assertEqual(event.table, "test")
        self.assertEqual(event.columns[1].name, 'data')

    def test_delete_row_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('Hello World')"
        self.execute(query)

        self.resetBinLog()

        query = "DELETE FROM test WHERE id = 1"
        self.execute(query)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()
        #FormatDescription
        self.stream.fetchone()

        #QueryEvent for the BEGIN
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, TableMapEvent)

        event = self.stream.fetchone()
        if self.isMySQL56AndMore():
            self.assertEqual(event.event_type, DELETE_ROWS_EVENT)
        else:
            self.assertEqual(event.event_type, DELETE_ROWS_EVENT_V1)
        self.assertIsInstance(event, DeleteRowsEvent)
        self.assertEqual(event.rows[0]["values"]["id"], 1)
        self.assertEqual(event.rows[0]["values"]["data"], "Hello World")

    def test_update_row_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('Hello')"
        self.execute(query)

        self.resetBinLog()

        query = "UPDATE test SET data = 'World' WHERE id = 1"
        self.execute(query)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()
        #FormatDescription
        self.stream.fetchone()

        #QueryEvent for the BEGIN
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, TableMapEvent)

        event = self.stream.fetchone()
        if self.isMySQL56AndMore():
            self.assertEqual(event.event_type, UPDATE_ROWS_EVENT)
        else:
            self.assertEqual(event.event_type, UPDATE_ROWS_EVENT_V1)
        self.assertIsInstance(event, UpdateRowsEvent)
        self.assertEqual(event.rows[0]["before_values"]["id"], 1)
        self.assertEqual(event.rows[0]["before_values"]["data"], "Hello")
        self.assertEqual(event.rows[0]["after_values"]["id"], 1)
        self.assertEqual(event.rows[0]["after_values"]["data"], "World")

class TestMultipleRowBinLogStreamReader(base.PyMySQLReplicationTestCase):
    def test_insert_multiple_row_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)

        self.resetBinLog()

        query = "INSERT INTO test (data) VALUES('Hello'),('World')"
        self.execute(query)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()
        #FormatDescription
        self.stream.fetchone()

        #QueryEvent for the BEGIN
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, TableMapEvent)

        event = self.stream.fetchone()
        if self.isMySQL56AndMore():
            self.assertEqual(event.event_type, WRITE_ROWS_EVENT)
        else:
            self.assertEqual(event.event_type, WRITE_ROWS_EVENT_V1)
        self.assertIsInstance(event, WriteRowsEvent)
        self.assertEqual(len(event.rows), 2)
        self.assertEqual(event.rows[0]["values"]["id"], 1)
        self.assertEqual(event.rows[0]["values"]["data"], "Hello")

        self.assertEqual(event.rows[1]["values"]["id"], 2)
        self.assertEqual(event.rows[1]["values"]["data"], "World")

    def test_update_multiple_row_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('Hello')"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('World')"
        self.execute(query)

        self.resetBinLog()

        query = "UPDATE test SET data = 'Toto'"
        self.execute(query)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()
        #FormatDescription
        self.stream.fetchone()

        #QueryEvent for the BEGIN
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, TableMapEvent)

        event = self.stream.fetchone()
        if self.isMySQL56AndMore():
           self.assertEqual(event.event_type, UPDATE_ROWS_EVENT)
        else:
           self.assertEqual(event.event_type, UPDATE_ROWS_EVENT_V1)
        self.assertIsInstance(event, UpdateRowsEvent)
        self.assertEqual(len(event.rows), 2)
        self.assertEqual(event.rows[0]["before_values"]["id"], 1)
        self.assertEqual(event.rows[0]["before_values"]["data"], "Hello")
        self.assertEqual(event.rows[0]["after_values"]["id"], 1)
        self.assertEqual(event.rows[0]["after_values"]["data"], "Toto")

        self.assertEqual(event.rows[1]["before_values"]["id"], 2)
        self.assertEqual(event.rows[1]["before_values"]["data"], "World")
        self.assertEqual(event.rows[1]["after_values"]["id"], 2)
        self.assertEqual(event.rows[1]["after_values"]["data"], "Toto")

    def test_delete_multiple_row_event(self):
        query = "CREATE TABLE test (id INT NOT NULL AUTO_INCREMENT, data VARCHAR (50) NOT NULL, PRIMARY KEY (id))"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('Hello')"
        self.execute(query)
        query = "INSERT INTO test (data) VALUES('World')"
        self.execute(query)

        self.resetBinLog()

        query = "DELETE FROM test"
        self.execute(query)
        self.execute("COMMIT")

        #RotateEvent
        self.stream.fetchone()
        #FormatDescription
        self.stream.fetchone()

        #QueryEvent for the BEGIN
        self.stream.fetchone()

        event = self.stream.fetchone()
        self.assertIsInstance(event, TableMapEvent)

        event = self.stream.fetchone()
        if self.isMySQL56AndMore():
            self.assertEqual(event.event_type, DELETE_ROWS_EVENT)
        else:
            self.assertEqual(event.event_type, DELETE_ROWS_EVENT_V1)
        self.assertIsInstance(event, DeleteRowsEvent)
        self.assertEqual(len(event.rows), 2)
        self.assertEqual(event.rows[0]["values"]["id"], 1)
        self.assertEqual(event.rows[0]["values"]["data"], "Hello")

        self.assertEqual(event.rows[1]["values"]["id"], 2)
        self.assertEqual(event.rows[1]["values"]["data"], "World")

__all__ = ["TestBasicBinLogStreamReader", "TestMultipleRowBinLogStreamReader"]

if __name__ == "__main__":
    import unittest
    unittest.main()
