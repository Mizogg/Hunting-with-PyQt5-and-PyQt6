import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QHBoxLayout, QComboBox, QProgressBar,QTextEdit
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
        self.setGeometry(60, 100, 300, 100)
        self.setWindowTitle('Hunter QT with Mizogg ICE Version')

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
        radio_button_layout = QHBoxLayout()
        self.random_button = QRadioButton('Random')
        self.random_button.setChecked(True)
        self.sequence_button = QRadioButton('Sequence')
        self.reverse_button = QRadioButton('Reverse')
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.random_button)
        self.button_group.addButton(self.sequence_button)
        self.button_group.addButton(self.reverse_button)
        radio_button_layout.addWidget(self.random_button)
        radio_button_layout.addWidget(self.sequence_button)
        radio_button_layout.addWidget(self.reverse_button)
        
        self.format_combo_box = QComboBox()
        self.format_combo_box.addItem("Decimal")
        self.format_combo_box.addItem("Hexadecimal")
        self.format_combo_box.addItem("Bits")
        radio_button_layout.addWidget(self.format_combo_box)
        
        self.format_combo_box_POWER = QComboBox()
        self.format_combo_box_POWER.addItem("1")
        self.format_combo_box_POWER.addItem("128")
        self.format_combo_box_POWER.addItem("256")
        self.format_combo_box_POWER.addItem("512")
        radio_button_layout.addWidget(self.format_combo_box_POWER)
        
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
        start_label = QLabel('Start Hexadecimal Decimal or Bit value:')
        start_label.setStyleSheet("color: green")
        self.start_edit = QLineEdit('1')
        self.start_edit.setStyleSheet("color: green")
        
        # Create a label and line edit for the Bit end value
        end_label = QLabel('End Hexadecimal Decimal or Bit value :')
        end_label.setStyleSheet("color: red")
        self.end_edit = QLineEdit('115792089237316195423570985008687907852837564279074904382605163141518161494336')
        self.end_edit.setStyleSheet("color: red")
        
        # Create a label and line edit for the Dec value
        dec_label = QLabel(' Dec value :')
        self.value_edit_dec = QLineEdit()
        self.value_edit_dec.setReadOnly(True)
        
        # Create a label and line edit for the HEX value
        hex_label = QLabel(' HEX value :')
        self.value_edit_hex = QLineEdit()
        self.value_edit_hex.setReadOnly(True)

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

        # Add horizontal layout to hold total keys scanned and keys per second
        keys_layout = QHBoxLayout()
        
        # Add total keys scanned label and line edit to horizontal layout
        found_keys_scanned_label = QLabel('Found')
        self.found_keys_scanned_edit = QLineEdit()
        self.found_keys_scanned_edit.setReadOnly(True)
        self.found_keys_scanned_edit.setText('0')  # Set initial value to 0
        keys_layout.addWidget(found_keys_scanned_label)
        keys_layout.addWidget(self.found_keys_scanned_edit)
        
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

        try:
            with open('start_scanned_key.txt', 'r') as f:
                saved_key_start = f.read()
            self.start_edit.setText(saved_key_start)
        except FileNotFoundError:
            pass
        try:
            with open('end_scanned_key.txt', 'r') as f:
                saved_key_end = f.read()
            self.end_edit.setText(saved_key_end)
        except FileNotFoundError:
            pass
        
    def start(self):
        power_format = self.format_combo_box_POWER.currentText()
        self.power_format = int(power_format)
        key_format = self.format_combo_box.currentText()
        start_value = self.start_edit.text()
        end_value = self.end_edit.text()
        if key_format == "Hexadecimal":
            start = int(start_value, 16)
            end = int(end_value, 16)
        elif key_format == "Decimal":
            start = int(start_value)
            end = int(end_value)
        elif key_format == "Bits":
            start = 2**(int(start_value))
            end = 2**(int(end_value))
        self.scanning = True
        if self.random_button.isChecked():
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        elif self.sequence_button.isChecked():
            self.current = start
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_sequence(key_format))
        elif self.reverse_button.isChecked():
            self.current = end
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_reverse(key_format))
        self.timer.start()
        # Set start time to current time in seconds
        self.start_time = time.time()
        # Connect timer's timeout signal to update_keys_per_sec method
        self.timer.timeout.connect(self.update_keys_per_sec)

    def stop(self):
        self.timer.stop()
        self.scanning = False
        
    def generate_crypto(self):
        found = int(self.found_keys_scanned_edit.text())
        startPrivKey = self.num
        for i in range (0,self.power_format):
            dec = int(startPrivKey)
            HEX = "%064x" % dec
            caddr = ice.privatekey_to_address(0, True, dec)
            uaddr = ice.privatekey_to_address(0, False, dec)
            p2sh = ice.privatekey_to_address(1, True, dec)
            bech32 = ice.privatekey_to_address(2, True, dec)
            ethaddr = ice.privatekey_to_ETH_address(dec)
            if caddr in bloom_filterbtc:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                WINTEXT = f'\n {caddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
                print(WINTEXT)
                with open("foundcaddr.txt", "a") as f:
                    f.write(WINTEXT)
            if uaddr in bloom_filterbtc:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                WINTEXT = f'\n {uaddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
                print(WINTEXT)
                with open("founduaddr.txt", "a") as f:
                    f.write(WINTEXT)
            if p2sh in bloom_filterbtc:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                WINTEXT = f'\n {p2sh}\nDecimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                print(WINTEXT)
                with open("foundp2sh.txt", "a") as f:
                    f.write(WINTEXT)
            if bech32 in bloom_filterbtc:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                WINTEXT = f'\n {bech32}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                print(WINTEXT)
                with open("foundbech32.txt", "a") as f:
                    f.write(WINTEXT)
            if ethaddr[2:] in bloom_filtereth:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                WINTEXT = f'\n {ethaddr}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                print(WINTEXT)
                with open("foundeth.txt", "a") as f:
                    f.write(WINTEXT)
            startPrivKey+=1
        # Update the text edits with the generated keys and addresses
        self.value_edit_dec.setText(str(dec))
        self.value_edit_hex.setText(HEX)
        if self.sequence_button.isChecked():
            with open('start_scanned_key.txt', 'w') as f:
                f.write(str(dec))
        elif self.reverse_button.isChecked():
            with open('end_scanned_key.txt', 'w') as f:
                f.write(str(dec))
        
    def update_display(self, start, end):
        if not self.scanning:
            self.timer.stop()
            return
        rng = random.SystemRandom()
        self.num = rng.randint(start, end)
        self.generate_crypto()
        self.counter += self.power_format

    def update_display_sequence(self, key_format):
        self.num = self.current
        if key_format == "Hexadecimal":
            if self.current > int(self.end_edit.text(), 16):
                self.timer.stop()
                self.scanning = False
                return
        elif key_format == "Decimal":
            if self.current > int(self.end_edit.text()):
                self.timer.stop()
                self.scanning = False
                return
        elif key_format == "Bits":
            if self.current > 2**(int(self.end_edit.text())):
                self.timer.stop()
                self.scanning = False
                return
        self.generate_crypto()
        self.current += self.power_format
        self.counter += self.power_format

    def update_display_reverse(self, key_format):
        self.num = self.current
        if key_format == "Hexadecimal":
            if self.current < int(self.start_edit.text(), 16):
                self.timer.stop()
                self.scanning = False
                return
        elif key_format == "Decimal":
            if self.current < int(self.start_edit.text()):
                self.timer.stop()
                self.scanning = False
                return
        elif key_format == "Bits":
            if self.current < 2**(int(self.start_edit.text())):
                self.timer.stop()
                self.scanning = False
                return
        self.generate_crypto()
        self.current -= self.power_format
        self.counter += self.power_format
    
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