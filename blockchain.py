# Программа на Python для создания блокчейна
# Для временной метки
import datetime
# Вычисление хэша для добавления цифровой подписи к блокам
import hashlib
# Для хранения данных в блокчейне
import json
import pandas as pd
# Flask предназначен для создания веб-приложения, а jsonify - для
# отображения блокчейнаn
from flask import Flask, jsonify
import mysql.connector
from mysql.connector import Error
import numpy as np
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
connection = create_connection("localhost", "root", "password", "block")


class Blockchain:
# Эта функция ниже создана для создания самого первого блока и установки его хэша равным "0"

    def __init__(self):
        self.chain = []
        self.create_block(proof=1, previous_hash='0')


# Эта функция ниже создана для добавления дополнительных блоков в цепочку
    def create_block(self, proof, previous_hash):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE mined=0 LIMIT 1")
        row = cursor.fetchone()
        if row:
            name = row[1]
            age = row[2]
            sex = row[3]
            salary = row[4]
            insurance = row[5]

            block = {'index': len(self.chain) + 1,
                        'timestamp': str(datetime.datetime.now()),
                        'name': name,
                        'age': age,
                        'sex': sex,
                        'salary': salary,
                        'insurance': insurance,
                        'proof': proof,
                        'previous_hash': previous_hash}
            self.chain.append(block)
            cursor.execute("UPDATE users SET mined=1 WHERE id=%s", (row[0],))  # Помечаем данные как "промайненные"
            connection.commit()
            return block
        else:  # Если больше данных для майнинга нет
            return None



# Эта функция ниже создана для отображения предыдущего блока
    def print_previous_block(self):
        return self.chain[-1]
# Это функция для проверки работы и используется для успешного майнинга блока
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(
                str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:5] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True
# Создание веб-приложения с использованием flask
app = Flask(__name__)
# Создаем объект класса blockchain
blockchain = Blockchain()
# Майнинг нового блока
@app.route('/mine_block', methods=['GET'])
def mine_block():
    previous_block = blockchain.print_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'A block is MINED',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

# Отобразить блокчейн в формате json
@app.route('/display_chain', methods=['GET'])
def display_chain():
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
        return jsonify(response), 200
# Проверка валидности блокчейна
@app.route('/valid', methods=['GET'])
def valid():
    valid = blockchain.chain_valid(blockchain.chain)
    if valid:
        response = {'message': 'The Blockchain is valid.'}
    else:
        response = {'message': 'The Blockchain is not valid.'}
    return jsonify(response), 200

# Запустите сервер flask локально
app.run(host='127.0.0.1', port=5000)

