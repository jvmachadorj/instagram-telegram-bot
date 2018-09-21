import peewee

from models import Image

if __name__ == '__main__':

    try:
        Image.create_table()
    except peewee.OperationalError:
        print('Tabela já existe')
