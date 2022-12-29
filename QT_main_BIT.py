import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QHBoxLayout
from PyQt5.QtCore import QTimer
from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
import secp256k1 as ice
import time
with open('btc.bf', "rb") as fp:
    bloom_filterbtc = BloomFilter.load(fp)

with open('eth.bf', "rb") as fp:
    bloom_filtereth = BloomFilter.load(fp)
    
app = QApplication(sys.argv)

class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a grid layout to hold the instances of the GUI
        grid_layout = QGridLayout()

        # Create instances of the GUI and add them to the grid layout
        for row in range(1): # Change here the ammount
            for col in range(1): # Change here the ammount
                instance = GUIInstance(row, col)
                grid_layout.addWidget(instance, row, col)

        # Set the main window's layout to the grid layout
        self.setLayout(grid_layout)
        self.setGeometry(60, 100, 200, 10)
        self.setWindowTitle('Hunter QT with Mizogg BIT Version')

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
        
        # Create a label and line edit for the Bit start value
        start_label = QLabel('Start Bit value:')
        start_label.setStyleSheet("color: green")
        self.start_edit = QLineEdit('1')
        self.start_edit.setStyleSheet("color: green")
        
        # Create a label and line edit for the Bit end value
        end_label = QLabel('End Bit value Max 256:')
        end_label.setStyleSheet("color: red")
        self.end_edit = QLineEdit('256')
        self.end_edit.setStyleSheet("color: red")
        
        # Create a label and line edit for the Dec value
        dec_label = QLabel(' Dec value :')
        self.value_edit_dec = QLineEdit()
        self.value_edit_dec.setReadOnly(True)
        
        # Create a label and line edit for the HEX value
        hex_label = QLabel(' HEX value :')
        self.value_edit_hex = QLineEdit()
        self.value_edit_hex.setReadOnly(True)
        
        # Create a label and line edit for the uncompressed address
        uncompressed_address_label = QLabel('Uncompressed address:')
        self.uncompressed_address_edit = QLineEdit()
        self.uncompressed_address_edit.setReadOnly(True)

        # Create a label and line edit for the compressed address
        compressed_address_label = QLabel('Compressed address:')
        self.compressed_address_edit = QLineEdit()
        self.compressed_address_edit.setReadOnly(True)
        
        # Create a label and line edit for the p2sh address
        p2sh_address_label = QLabel('p2sh address:')
        self.p2sh_address_edit = QLineEdit()
        self.p2sh_address_edit.setReadOnly(True)

        # Create a label and line edit for the bc1 address
        bech32_address_label = QLabel('bech32 address:')
        self.bech32_address_edit = QLineEdit()
        self.bech32_address_edit.setReadOnly(True)
        
        # Create a label and line edit for the ETH address
        ethaddr_address_label = QLabel('Eth address:')
        self.ethaddr_address_edit = QLineEdit()
        self.ethaddr_address_edit.setReadOnly(True)
        
        # Set the layout
        layout = QVBoxLayout()
        layout.addLayout(radio_button_layout)
        layout.addWidget(start_label)
        layout.addWidget(self.start_edit)
        layout.addWidget(end_label)
        layout.addWidget(self.end_edit)
        layout.addWidget(dec_label)
        layout.addWidget(self.value_edit_dec)
        layout.addWidget(hex_label)
        layout.addWidget(self.value_edit_hex)
        layout.addWidget(uncompressed_address_label)
        layout.addWidget(self.uncompressed_address_edit)
        layout.addWidget(compressed_address_label)
        layout.addWidget(self.compressed_address_edit)
        layout.addWidget(p2sh_address_label)
        layout.addWidget(self.p2sh_address_edit)
        layout.addWidget(bech32_address_label)
        layout.addWidget(self.bech32_address_edit)
        layout.addWidget(ethaddr_address_label)
        layout.addWidget(self.ethaddr_address_edit)
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
        start_bit = self.start_edit.text()
        end_bit = self.end_edit.text()
        start = 2**(int(start_bit))
        end = 2**(int(end_bit))
        self.scanning = True
        if self.random_button.isChecked():
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        else:
            self.current = start
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_display_sequence)
        self.timer.start(1)
        self.start_time = time.time()
        self.timer.timeout.connect(self.update_keys_per_sec)

    def stop(self):
        self.timer.stop()
        self.scanning = False

    def update_display(self, start, end):
        if not self.scanning:
            self.timer.stop()
            return
        rng = random.SystemRandom()
        dec = rng.randint(start, end)
        HEX = "%064x" % dec
        caddr = ice.privatekey_to_address(0, True, dec)
        uaddr = ice.privatekey_to_address(0, False, dec)
        p2sh = ice.privatekey_to_address(1, True, dec)
        bech32 = ice.privatekey_to_address(2, True, dec)
        ethaddr = ice.privatekey_to_ETH_address(dec)
        self.value_edit_dec.setText(str(dec))
        self.value_edit_hex.setText(HEX)
        self.uncompressed_address_edit.setText(uaddr)
        self.compressed_address_edit.setText(caddr)
        self.p2sh_address_edit.setText(p2sh)
        self.bech32_address_edit.setText(bech32)
        self.ethaddr_address_edit.setText(ethaddr)
        if caddr in bloom_filterbtc:
            WINTEXT = f'\n {caddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
            print(WINTEXT)
            with open("foundcaddr.txt", "a") as f:
                f.write(WINTEXT)
        if uaddr in bloom_filterbtc:
            WINTEXT = f'\n {uaddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
            print(WINTEXT)
            with open("founduaddr.txt", "a") as f:
                f.write(WINTEXT)
        if p2sh in bloom_filterbtc:
            WINTEXT = f'\n {p2sh}\nDecimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
            print(WINTEXT)
            with open("foundp2sh.txt", "a") as f:
                f.write(WINTEXT)
        if bech32 in bloom_filterbtc:
            WINTEXT = f'\n {bech32}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
            print(WINTEXT)
            with open("foundbech32.txt", "a") as f:
                f.write(WINTEXT)
        if ethaddr[2:] in bloom_filtereth:
            WINTEXT = f'\n {ethaddr}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
            print(WINTEXT)
            with open("foundeth.txt", "a") as f:
                f.write(WINTEXT)
        self.counter += 1

    def update_display_sequence(self):
        dec = self.current
        self.current += 1
        end_bit = self.end_edit.text()
        if self.current > 2**(int(end_bit)):
            self.timer.stop()
            self.scanning = False
            return
        HEX = "%064x" % dec
        caddr = ice.privatekey_to_address(0, True, dec)
        uaddr = ice.privatekey_to_address(0, False, dec)
        p2sh = ice.privatekey_to_address(1, True, dec)
        bech32 = ice.privatekey_to_address(2, True, dec)
        ethaddr = ice.privatekey_to_ETH_address(dec)
        self.value_edit_dec.setText(str(dec))
        self.value_edit_hex.setText(HEX)
        self.uncompressed_address_edit.setText(uaddr)
        self.compressed_address_edit.setText(caddr)
        self.p2sh_address_edit.setText(p2sh)
        self.bech32_address_edit.setText(bech32)
        self.ethaddr_address_edit.setText(ethaddr)
        if caddr in bloom_filterbtc:
            WINTEXT = f'\n {caddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
            print(WINTEXT)
            with open("foundcaddr.txt", "a") as f:
                f.write(WINTEXT)
        if uaddr in bloom_filterbtc:
            WINTEXT = f'\n {uaddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
            print(WINTEXT)
            with open("founduaddr.txt", "a") as f:
                f.write(WINTEXT)
        if p2sh in bloom_filterbtc:
            WINTEXT = f'\n {p2sh}\nDecimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
            print(WINTEXT)
            with open("foundp2sh.txt", "a") as f:
                f.write(WINTEXT)
        if bech32 in bloom_filterbtc:
            WINTEXT = f'\n {bech32}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
            print(WINTEXT)
            with open("foundbech32.txt", "a") as f:
                f.write(WINTEXT)
        if ethaddr[2:] in bloom_filtereth:
            WINTEXT = f'\n {ethaddr}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
            print(WINTEXT)
            with open("foundeth.txt", "a") as f:
                f.write(WINTEXT)
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
