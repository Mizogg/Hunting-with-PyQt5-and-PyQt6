import sys
import random
import ecdsa
import hashlib
import base58
import mnemonic
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QRadioButton, QButtonGroup
from PyQt5.QtCore import QTimer
from mnemonic import Mnemonic
import requests
app = QApplication(sys.argv)

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a radio button group for the random and sequence options
        radio_button_layout = QVBoxLayout()
        self.random_button = QRadioButton('Random')
        self.random_button.setChecked(True)
        self.sequence_button = QRadioButton('Sequence')
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.random_button)
        self.button_group.addButton(self.sequence_button)
        radio_button_layout.addWidget(self.random_button)
        radio_button_layout.addWidget(self.sequence_button)

        # Create a label and line edit for the start hex value
        start_label = QLabel('Start hex value:')
        start_label.setStyleSheet("color: green")
        self.start_edit = QLineEdit('1')
        self.start_edit.setStyleSheet("color: green")

        # Create a label and line edit for the end hex value
        end_label = QLabel('End hex value:')
        end_label.setStyleSheet("color: red")
        self.end_edit = QLineEdit('fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141')
        self.end_edit.setStyleSheet("color: red")

        # Create a Start button
        start_button = QPushButton('Start')
        start_button.setStyleSheet("color: green")
        start_button.clicked.connect(self.start)

        # Create a Stop button
        stop_button = QPushButton('Stop')
        stop_button.setStyleSheet("color: red")
        stop_button.clicked.connect(self.stop)

        # Create a label and line edit for the private key
        private_key_label = QLabel('Private key:')
        self.private_key_edit = QLineEdit()
        self.private_key_edit.setReadOnly(True)

        # Create a label and line edit for the mnemonic phrase
        mnemonic_phrase_label = QLabel('Mnemonic phrase:')
        self.mnemonic_phrase_edit = QLineEdit()
        self.mnemonic_phrase_edit.setReadOnly(True)

        # Create a label and line edit for the uncompressed address
        uncompressed_address_label = QLabel('Uncompressed address:')
        self.uncompressed_address_edit = QLineEdit()
        self.uncompressed_address_edit.setReadOnly(True)

        # Create a label and line edit for the compressed address
        compressed_address_label = QLabel('Compressed address:')
        self.compressed_address_edit = QLineEdit()
        self.compressed_address_edit.setReadOnly(True)

        # Set the layout
        layout = QVBoxLayout()
        layout.addLayout(radio_button_layout)
        layout.addWidget(start_label)
        layout.addWidget(self.start_edit)
        layout.addWidget(end_label)
        layout.addWidget(self.end_edit)
        layout.addWidget(start_button)
        layout.addWidget(stop_button)
        layout.addWidget(private_key_label)
        layout.addWidget(self.private_key_edit)
        layout.addWidget(mnemonic_phrase_label)
        layout.addWidget(self.mnemonic_phrase_edit)
        layout.addWidget(uncompressed_address_label)
        layout.addWidget(self.uncompressed_address_edit)
        layout.addWidget(compressed_address_label)
        layout.addWidget(self.compressed_address_edit)
        self.setLayout(layout)
        self.setGeometry(100, 60, 1000, 400)
        self.setWindowTitle('Hunter QT ON-Line with Mizogg ')

    def start(self):
        # Get the start and end hex values from the line edits
        start_hex = self.start_edit.text()
        end_hex = self.end_edit.text()

        # Convert the hexadecimal values to integers
        start = int(start_hex, 16)
        end = int(end_hex, 16)
        self.scanning = True

        # Check which radio button is selected
        if self.random_button.isChecked():
            # Set the current value to a random value between the start and end values
            self.current = random.randint(start, end)

            # Create a QTimer object and connect its timeout signal to the update_display slot
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        else:
            # Set the current value to the start value
            self.current = start

            # Create a QTimer object and connect its timeout signal to the update_display_sequence slot
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_display_sequence)

        # Start the timer
        self.timer.start(1)

    def stop(self):
        # Stop the timer
        self.timer.stop()
        self.scanning = False

    def update_display(self, start, end):
        # Check if the 'Stop' button has been clicked
        if not self.scanning:
            # Stop the timer if the 'Stop' button has been clicked
            self.timer.stop()
            return

        # Create a SystemRandom object
        rng = random.SystemRandom()

        # Generate a random private key within the specified range
        private_key = rng.randint(start, end)
        private_key = private_key.to_bytes(32, 'big')

        # Use the ecdsa library to create a public key from the private key
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()

        # Generate an uncompressed public key
        public_key_uncompressed = b'\04' + vk.to_string()

        # Generate a compressed public key
        if vk.pubkey.point.y() % 2 == 0:
            public_key_compressed = b'\02' + vk.to_string()[:32]
        else:
            public_key_compressed = b'\03' + vk.to_string()[:32]

        # Hash the uncompressed public key using SHA256 and RIPEMD160 to create a 20-byte hash160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(public_key_uncompressed).digest())
        hash160_uncompressed = ripemd160.digest()

        # Hash the compressed public key using SHA256 and RIPEMD160 to create a 20-byte hash160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(public_key_compressed).digest())
        hash160_compressed = ripemd160.digest()

        # Add a version byte and checksum to the hash160 to create a 25-byte binary Bitcoin address
        version_byte = b'\00'
        binary_address_uncompressed = version_byte + hash160_uncompressed
        binary_address_compressed = version_byte + hash160_compressed
        checksum = hashlib.sha256(hashlib.sha256(binary_address_uncompressed).digest()).digest()[:4]
        binary_address_uncompressed += checksum
        checksum = hashlib.sha256(hashlib.sha256(binary_address_compressed).digest()).digest()[:4]
        binary_address_compressed += checksum

        # Encode the binary addresses as base58 strings
        base58_address_uncompressed = base58.b58encode(binary_address_uncompressed)
        base58_address_compressed = base58.b58encode(binary_address_compressed)

        # Create a Mnemonic object with the English wordlist
        mnemo = mnemonic.Mnemonic("english")

        # Convert the private key to a mnemonic phrase
        mnemonic_phrase = mnemo.to_mnemonic(private_key)

        # Display the private key, mnemonic phrase, and addresses in the line edits
        self.private_key_edit.setText(private_key.hex())
        self.mnemonic_phrase_edit.setText(mnemonic_phrase)
        response = requests.get("https://blockstream.info/api/address/" + str(base58_address_compressed.decode()))
        balance = float(response.json()['chain_stats']['funded_txo_sum'])
        totalSent = float(response.json()['chain_stats']['spent_txo_sum'])
        txs = response.json()['chain_stats']['funded_txo_count']
        source_code = f'{base58_address_compressed.decode()} TotalReceived = [{balance}] : TotalSent =  [{totalSent}] : Transactions = [{txs}]'
        
        responseu = requests.get("https://blockstream.info/api/address/" + str(base58_address_uncompressed.decode()))
        balanceu = float(responseu.json()['chain_stats']['funded_txo_sum'])
        totalSentu = float(responseu.json()['chain_stats']['spent_txo_sum'])
        txsu = responseu.json()['chain_stats']['funded_txo_count']
        source_codeu = f'{base58_address_uncompressed.decode()} TotalReceived = [{balanceu}] : TotalSent =  [{totalSentu}] : Transactions = [{txsu}]'
        self.uncompressed_address_edit.setText(source_code)
        self.compressed_address_edit.setText(source_codeu)
        if int(txs) > 0:
            print ('winner')
            with open('found.txt', 'a') as result:
                result.write(f'\n Hex Key: {private_key.hex()}\n Mnemonic {mnemonic_phrase} \nBTC Address Compressed: {source_code} \nBTC Address Uncompressed: {source_codeu}')

    def update_display_sequence(self):
        # Generate a private key from the current value
        private_key = hex(self.current)[2:]
        self.current += 1

        # Check if the current value is greater than the end value
        if self.current > int(self.end_edit.text(), 16):
            # Stop the timer
            self.timer.stop()
            self.scanning = False
            return

        # Use a regular expression to remove any non-hexadecimal characters from the private_key string
        # Convert the private key to a bytes object
        private_key = int(private_key, 16)
        private_key = private_key.to_bytes(32, 'big')

        # Use the ecdsa library to create a public key from the private key
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()

        # Generate an uncompressed public key
        public_key_uncompressed = b'\04' + vk.to_string()

        # Generate a compressed public key
        if vk.pubkey.point.y() % 2 == 0:
            public_key_compressed = b'\02' + vk.to_string()[:32]
        else:
            public_key_compressed = b'\03' + vk.to_string()[:32]

        # Hash the uncompressed public key using SHA256 and RIPEMD160 to create a 20-byte hash160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(public_key_uncompressed).digest())
        hash160_uncompressed = ripemd160.digest()

        # Hash the compressed public key using SHA256 and RIPEMD160 to create a 20-byte hash160
        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(hashlib.sha256(public_key_compressed).digest())
        hash160_compressed = ripemd160.digest()

        # Add a version byte and checksum to the hash160 to create a 25-byte binary Bitcoin address
        version_byte = b'\00'
        binary_address_uncompressed = version_byte + hash160_uncompressed
        binary_address_compressed = version_byte + hash160_compressed
        checksum = hashlib.sha256(hashlib.sha256(binary_address_uncompressed).digest()).digest()[:4]
        binary_address_uncompressed += checksum
        checksum = hashlib.sha256(hashlib.sha256(binary_address_compressed).digest()).digest()[:4]
        binary_address_compressed += checksum

        # Encode the binary addresses as base58 strings
        base58_address_uncompressed = base58.b58encode(binary_address_uncompressed)
        base58_address_compressed = base58.b58encode(binary_address_compressed)

        # Create a Mnemonic object with the English wordlist
        mnemo = mnemonic.Mnemonic("english")

        # Convert the private key to a mnemonic phrase
        mnemonic_phrase = mnemo.to_mnemonic(private_key)

        # Display the private key, mnemonic phrase, and addresses in the line edits
        self.private_key_edit.setText(private_key.hex())
        self.mnemonic_phrase_edit.setText(mnemonic_phrase)
        response = requests.get("https://blockstream.info/api/address/" + str(base58_address_compressed.decode()))
        balance = float(response.json()['chain_stats']['funded_txo_sum'])
        totalSent = float(response.json()['chain_stats']['spent_txo_sum'])
        txs = response.json()['chain_stats']['funded_txo_count']
        source_code = f'{base58_address_compressed.decode()} TotalReceived = [{balance}] : TotalSent =  [{totalSent}] : Transactions = [{txs}]'
        
        responseu = requests.get("https://blockstream.info/api/address/" + str(base58_address_uncompressed.decode()))
        balanceu = float(responseu.json()['chain_stats']['funded_txo_sum'])
        totalSentu = float(responseu.json()['chain_stats']['spent_txo_sum'])
        txsu = responseu.json()['chain_stats']['funded_txo_count']
        source_codeu = f'{base58_address_uncompressed.decode()} TotalReceived = [{balanceu}] : TotalSent =  [{totalSentu}] : Transactions = [{txsu}]'
        self.uncompressed_address_edit.setText(source_code)
        self.compressed_address_edit.setText(source_codeu)
        if int(txs) > 0:
            print ('winner')
            with open('found.txt', 'a') as result:
                result.write(f'\n Hex Key: {private_key.hex()}\n Mnemonic {mnemonic_phrase} \nBTC Address Compressed: {source_code} \nBTC Address Uncompressed: {source_codeu}')

if __name__ == '__main__':
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
