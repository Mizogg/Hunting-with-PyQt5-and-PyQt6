import sys
import random
import ecdsa
import hashlib
import base58
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QHBoxLayout
from PyQt5.QtCore import QTimer
from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
import time
with open('btc.bf', "rb") as fp:
    bloom_filterbtc = BloomFilter.load(fp)
app = QApplication(sys.argv)

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a grid layout to hold the instances of the GUI
        grid_layout = QGridLayout()

        # Create instances of the GUI and add them to the grid layout
        for row in range(2): # Change here the ammount
            for col in range(2): # Change here the ammount
                instance = GUIInstance(row, col)
                grid_layout.addWidget(instance, row, col)

        # Set the main window's layout to the grid layout
        self.setLayout(grid_layout)
        self.setGeometry(60, 100, 200, 10)
        self.setWindowTitle('Hunter QT MAIN with Mizogg Version')
        
class GUIInstance(QWidget):
    def __init__(self, row, col):
        super().__init__()
        self.row = row
        self.col = col
        self.initUI()

    def initUI(self):
        # Create a horizontal layout for the radio buttons and start/stop buttons
        radio_button_layout = QHBoxLayout()
        
        # Create a radio button group for the random and sequence options
        self.random_button = QRadioButton('Random')
        self.random_button.setChecked(True)
        self.sequence_button = QRadioButton('Sequence')
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.random_button)
        self.button_group.addButton(self.sequence_button)
        radio_button_layout.addWidget(self.random_button)
        radio_button_layout.addWidget(self.sequence_button)
        
        # Create a Start button
        start_button = QPushButton('Start')
        start_button.setStyleSheet("color: green")
        start_button.clicked.connect(self.start)
        
        # Create a Stop button
        stop_button = QPushButton('Stop')
        stop_button.setStyleSheet("color: red")
        stop_button.clicked.connect(self.stop)
        
        # Add the start and stop buttons to the radio button layout
        radio_button_layout.addWidget(start_button)
        radio_button_layout.addWidget(stop_button)
        
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
        
        # Create a label and line edit for the private key
        private_key_label = QLabel('Private key:')
        self.private_key_edit = QLineEdit()
        self.private_key_edit.setReadOnly(True)
        
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
        layout.addWidget(private_key_label)
        layout.addWidget(self.private_key_edit)
        layout.addWidget(uncompressed_address_label)
        layout.addWidget(self.uncompressed_address_edit)
        layout.addWidget(compressed_address_label)
        layout.addWidget(self.compressed_address_edit)
        # Add horizontal layout to hold total keys scanned and keys per second
        keys_layout = QHBoxLayout()

        # Add total keys scanned label and line edit to horizontal layout
        total_keys_scanned_label = QLabel('Total keys scanned:')
        self.total_keys_scanned_edit = QLineEdit()
        self.total_keys_scanned_edit.setReadOnly(True)
        self.total_keys_scanned_edit.setText('0')  # Set initial value to 0
        keys_layout.addWidget(total_keys_scanned_label)
        keys_layout.addWidget(self.total_keys_scanned_edit)

        # Add keys per second label and line edit to horizontal layout
        keys_per_sec_label = QLabel('Keys per second:')
        self.keys_per_sec_edit = QLineEdit()
        self.keys_per_sec_edit.setReadOnly(True)
        keys_layout.addWidget(keys_per_sec_label)
        keys_layout.addWidget(self.keys_per_sec_edit)

        # Add horizontal layout to main vertical layout
        layout.addLayout(keys_layout)

        self.setLayout(layout)
        # Initialize counter and timer variables
        self.counter = 0
        self.timer = time.time()

    def start(self):
        start_hex = self.start_edit.text()
        end_hex = self.end_edit.text()
        start = int(start_hex, 16)
        end = int(end_hex, 16)
        self.scanning = True
        if self.random_button.isChecked():
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        else:
            self.current = start
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_display_sequence)
        self.timer.start(1)

        # Set start time to current time in seconds
        self.start_time = time.time()

        # Connect timer's timeout signal to update_keys_per_sec method
        self.timer.timeout.connect(self.update_keys_per_sec)

    def stop(self):
        self.timer.stop()
        self.scanning = False

    def generate_crypto(self, private_key):
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

        # Display the private key, and addresses in the line edits
        self.private_key_edit.setText(private_key.hex())

        self.uncompressed_address_edit.setText(base58_address_uncompressed.decode())
        self.compressed_address_edit.setText(base58_address_compressed.decode())
        if  base58_address_compressed.decode() in bloom_filterbtc or base58_address_uncompressed.decode() in bloom_filterbtc:
            wintext = f'\n Hexadecimal Private Key \n {private_key.hex()}  \nBTC Address Compressed: {base58_address_compressed.decode()} \nBTC Address Uncompressed: {base58_address_uncompressed.decode()}'
            print (wintext)
            with open('found.txt', 'a') as result:
                result.write(wintext)
                
    def update_display(self, start, end):
        if not self.scanning:
            self.timer.stop()
            return
        rng = random.SystemRandom()
        private_key = rng.randint(start, end)
        private_key = private_key.to_bytes(32, 'big')
        self.generate_crypto(private_key)
        self.counter += 1

    def update_display_sequence(self):
        private_key = hex(self.current)[2:]
        self.current += 1
        if self.current > int(self.end_edit.text(), 16):
            self.timer.stop()
            self.scanning = False
            return
        private_key = int(private_key, 16)
        private_key = private_key.to_bytes(32, 'big')
        self.generate_crypto(private_key)
        self.counter += 1
    
    def update_keys_per_sec(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time == 0:
            keys_per_sec = 0
        else:
            keys_per_sec = self.counter / elapsed_time
        keys_per_sec = round(keys_per_sec, 2)
        self.keys_per_sec_edit.setText(str(keys_per_sec))
        self.start_time = time.time()
        total_keys_scanned = int(self.total_keys_scanned_edit.text()) + self.counter
        self.total_keys_scanned_edit.setText(str(total_keys_scanned))
        self.counter = 0

if __name__ == '__main__':
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())