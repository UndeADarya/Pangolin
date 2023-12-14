import unittest
import psycopg2
from psycopg2 import Error
import os


class DbTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        # Для прогона на разных стендах указать переменные окружения (export)
        try:
            self.connection = psycopg2.connect(user=os.environ.get('TEST_DB_USER', 'postgres'),
                                              password=os.environ.get('TEST_DB_PASS', 'postgres'),
                                              host=os.environ.get('TEST_DB_HOST', 'localhost'),
                                              port=os.environ.get('TEST_DB_PORT', '5432'),
                                              database=os.environ.get('TEST_DB_NAME', 'test_db'))
            self.cursor = self.connection.cursor()
        except (Exception, Error) as error:
            print("Ошибка при работе с PostgreSQL", error)
        # Тип данных поля "Index" выбран для автозаполнения
        # Тип данных поля "Name" - имя может содержать разные символы, длина в пределах разумного
        # Тип данных поля "DateOfBirth" - тип date предназначен для хранения даты, удобство сравнения и выборки в дальнейшем
        self.cursor.execute('''CREATE TABLE "People"
                             ("Index" SERIAL PRIMARY KEY NOT NULL,
                             "Name" VARCHAR(50) NOT NULL,
                             "DateOfBirth" DATE); ''')

    # Примеры тестов

    def test_insert1(self):
        self.cursor.execute(
            '''INSERT INTO "People" ("Name", "DateOfBirth") VALUES (%s, %s) RETURNING "Index"''',
            ('Den', '2022-11-11'))
        s = self.cursor.fetchone()[0]
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People" WHERE "Index" = %s''', str(s))
        res = self.cursor.fetchone()
        self.assertEqual(res[1], 'Den')
        self.assertEqual(str(res[2]), '2022-11-11')


    def test_insert2(self):
        self.cursor.execute(
            '''INSERT INTO "People" ("Index", "Name", "DateOfBirth") VALUES (%s, %s, %s)''',
            ('0', 'Д''Артаньян', '2022-11-11'))
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People" WHERE "Index" = %s AND "Name" = %s AND "DateOfBirth" = %s''',
                            ('0', 'Д''Артаньян', '2022-11-11'))
        res = self.cursor.fetchone()
        self.assertEqual(res[0], 0)
        self.assertEqual(res[1], 'Д''Артаньян')
        self.assertEqual(str(res[2]), '2022-11-11')


    def test_insert3(self):
        self.cursor.execute(
            '''INSERT INTO "People" ("Name") VALUES (%s)''', (' '))
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People" WHERE "Name" = %s''', (' '))
        res = self.cursor.fetchone()
        self.assertEqual(res[1], ' ')


    def test_insert4(self):
        self.cursor.execute(
            '''INSERT INTO "People" ("Index", "Name", "DateOfBirth") VALUES (%s, %s, %s)''',
            ('4', 'Anna Maria', '2023-12-12'))
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People" WHERE "Index" = %s AND "Name" = %s AND "DateOfBirth" = %s''',
                            ('4', 'Anna Maria', '2023-12-12'))
        res = self.cursor.fetchone()
        self.assertEqual(res[0], 4)
        self.assertEqual(res[1], 'Anna Maria')
        self.assertEqual(str(res[2]), '2023-12-12')


    def test_insert_neg1(self):
        with self.assertRaises (Error):
            self.cursor.execute(
                '''INSERT INTO "People" ("Index", "Name", "DateOfBirth") VALUES (%s, %s, %s)''',
                ('2', 'Den', '2023-12-12'))
        self.connection.rollback()

    #набор "негативных" инсертов
    #...


    def test_select(self):
        self.cursor.execute('''SELECT * FROM "People" WHERE "Index" = %s AND "Name" LIKE %s''',
                            ('4', '%Mar%'))
        res = self.cursor.fetchone()
        self.assertEqual(res[0], 4)
        self.assertEqual(res[1], 'Anna Maria')

    #набор селектов
    #...

    def test_update(self):
        self.cursor.execute(
            '''UPDATE "People" SET "Index" = %s, "Name" = %s, "DateOfBirth" = %s WHERE "Index" = %s''',
            ('6', 'Bob', '1901-01-10', '4'))
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People" WHERE "Index" = %s''',('6'))
        res = self.cursor.fetchone()
        self.assertEqual(res[1], 'Bob')
        self.assertEqual(str(res[2]), '1901-01-10')

    # набор апдейтов
    # ...

    def test_delete1(self):
        self.cursor.execute(
            '''DELETE FROM "People" WHERE "Index" = %s''',('6'))
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People" WHERE "Index" = %s''',('6'))
        res = self.cursor.fetchone()
        self.assertIs(res, None)


    def test_delete2(self):
        self.cursor.execute(
            '''DELETE FROM "People"''')
        self.connection.commit()
        self.cursor.execute('''SELECT * FROM "People"''')
        res = self.cursor.fetchone()
        self.assertIs(res, None)


    @classmethod
    def tearDownClass(self):
        self.cursor.execute('''DROP TABLE "People" CASCADE''')
        self.connection.commit()
        if self.connection:
            self.cursor.close()
            self.connection.close()


if __name__ == "__main__":
    unittest.main()


'''
Использовалось в процессе работы:

def generate(amount=50):
    connection = conn()
    cursor = connection.cursor()
    cursor.execute(''''''CREATE TABLE "People2"
                     ("Index" SERIAL PRIMARY KEY NOT NULL,
                     "Name" VARCHAR(50) NOT NULL,
                     "DateOfBirth" DATE); '''''')
    fake = Faker()
    i = print(fake.first_name())
    print(i)
    for i in range(amount):
        cursor.execute(''''''INSERT INTO "People" ("Name", "DateOfBirth") VALUES (%s, %s)''''''',
                            (fake.first_name(), fake.date()))
        print(fake.first_name())
    connection.commit()

generate(50)
'''