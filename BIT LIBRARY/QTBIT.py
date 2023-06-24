import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QRadioButton, QButtonGroup, QHBoxLayout, QComboBox, QProgressBar, QMessageBox
from PyQt5.QtCore import QTimer
from bit import Key
from bit.format import bytes_to_wif
import time
import webbrowser
import psutil
import multiprocessing

mizogg= '''
                      ___            ___  
                     (o o)          (o o) 
                    (  V  ) MIZOGG (  V  )
                    --m-m------------m-m--
                  © mizogg.co.uk 2018 - 2023
                    QTBIT.py CryptoHunter
'''
print(mizogg)

filename = 'puzzle.txt'
with open(filename) as file:
    addfind = file.read().split()

app = QApplication(sys.argv)


def run_app():
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.num = 0  # Add this line to initialize self.num
        self.initUI()

    def initUI(self):
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
        self.format_combo_box.addItem("Hexadecimal")
        self.format_combo_box.addItem("Decimal")
        self.format_combo_box.addItem("Bits")
        radio_button_layout.addWidget(self.format_combo_box)
        self.format_combo_box_POWER = QComboBox()
        self.format_combo_box_POWER.addItem("512")
        self.format_combo_box_POWER.addItem("256")
        self.format_combo_box_POWER.addItem("128")
        self.format_combo_box_POWER.addItem("1")
        radio_button_layout.addWidget(self.format_combo_box_POWER)
        start_button = QPushButton('Start')
        start_button.setStyleSheet("color: green")
        start_button.clicked.connect(self.start)
        stop_button = QPushButton('Stop')
        stop_button.setStyleSheet("color: red")
        stop_button.clicked.connect(self.stop)
        radio_button_layout.addWidget(start_button)
        radio_button_layout.addWidget(stop_button)
        start_label = QLabel('Start Hexadecimal Decimal or Bit value set to puzzle 66:')
        start_label.setStyleSheet("color: green")
        self.start_edit = QLineEdit('20000000000000000')
        self.start_edit.setStyleSheet("color: green")
        end_label = QLabel('End Hexadecimal Decimal or Bit value set to puzzle 66:')
        end_label.setStyleSheet("color: red")
        self.end_edit = QLineEdit('3ffffffffffffffff')
        self.end_edit.setStyleSheet("color: red")
        dec_label = QLabel(' Dec value :')
        self.value_edit_dec = QLineEdit()
        self.value_edit_dec.setReadOnly(True)
        hex_label = QLabel(' HEX value :')
        self.value_edit_hex = QLineEdit()
        self.value_edit_hex.setReadOnly(True)
        uncompressed_address_label = QLabel('Uncompressed address:')
        self.uncompressed_address_edit = QLineEdit()
        self.uncompressed_address_edit.setReadOnly(True)
        compressed_address_label = QLabel('Compressed address:')
        self.compressed_address_edit = QLineEdit()
        self.compressed_address_edit.setReadOnly(True)
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
        address_layout_caddr = QHBoxLayout()
        address_layout_caddr.addWidget(compressed_address_label)
        address_layout_caddr.addWidget(self.compressed_address_edit)
        open_button = QPushButton("Open in Browser")
        open_button.clicked.connect(lambda: self.open_browser(str(self.compressed_address_edit.text())))
        address_layout_caddr.addWidget(open_button)
        layout.addLayout(address_layout_caddr)
        address_layout_uaddr = QHBoxLayout()
        address_layout_uaddr.addWidget(uncompressed_address_label)
        address_layout_uaddr.addWidget(self.uncompressed_address_edit)
        open_button = QPushButton("Open in Browser")
        open_button.clicked.connect(lambda: self.open_browser(str(self.uncompressed_address_edit.text())))
        address_layout_uaddr.addWidget(open_button)
        layout.addLayout(address_layout_uaddr)
        keys_layout = QHBoxLayout()
        found_keys_scanned_label = QLabel('Found')
        self.found_keys_scanned_edit = QLineEdit()
        self.found_keys_scanned_edit.setReadOnly(True)
        self.found_keys_scanned_edit.setText('0')
        keys_layout.addWidget(found_keys_scanned_label)
        keys_layout.addWidget(self.found_keys_scanned_edit)
        total_keys_scanned_label = QLabel('Total keys scanned:')
        self.total_keys_scanned_edit = QLineEdit()
        self.total_keys_scanned_edit.setReadOnly(True)
        self.total_keys_scanned_edit.setText('0')
        keys_layout.addWidget(total_keys_scanned_label)
        keys_layout.addWidget(self.total_keys_scanned_edit)
        keys_per_sec_label = QLabel('Keys per second:')
        self.keys_per_sec_edit = QLineEdit()
        self.keys_per_sec_edit.setReadOnly(True)
        keys_layout.addWidget(keys_per_sec_label)
        keys_layout.addWidget(self.keys_per_sec_edit)
        layout.addLayout(keys_layout)
        self.setLayout(layout)
        self.counter = 0
        self.timer = time.time()
        power_layout_text = QHBoxLayout()
        CPU_label = QLabel('Python Avg CPU %')
        CPU_label_total = QLabel('CPU Total %')
        RAM_label = QLabel('RAM %')
        power_layout_text.addWidget(CPU_label)
        power_layout_text.addWidget(CPU_label_total)
        power_layout_text.addWidget(RAM_label)
        power_layout = QHBoxLayout()
        self.cpu_usage_bar = QProgressBar()
        self.cpu_usage_bar.setRange(0, 100)
        self.cpu_usage_total = QProgressBar()
        self.cpu_usage_total.setRange(0, 100)
        self.ram_usage_bar = QProgressBar()
        self.ram_usage_bar.setRange(0, 100)
        power_layout.addWidget(self.cpu_usage_bar)
        power_layout.addWidget(self.cpu_usage_total)
        power_layout.addWidget(self.ram_usage_bar)
        layout.addLayout(power_layout_text)
        layout.addLayout(power_layout)
        self.timer_cpu = QTimer()
        self.timer_cpu.timeout.connect(self.update_usage)
        self.timer_cpu.start(500)
        progress_layout_text = QHBoxLayout()
        progress_label = QLabel('progress %')
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout_text.addWidget(progress_label)
        progress_layout_text.addWidget(self.progress_bar)
        layout.addLayout(progress_layout_text)
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
        
    def update_usage(self):
        num_cores = psutil.cpu_count(logical=False)
        cpu_usage = psutil.cpu_percent()
        total_cpu_usage = int(cpu_usage * num_cores)
        self.cpu_usage_total.setValue(total_cpu_usage)
        self.cpu_usage_bar.setValue(int(cpu_usage))
        ram_usage = int(psutil.virtual_memory().percent)
        self.ram_usage_bar.setValue(ram_usage)

    
    def open_browser(self, address):
        url = f'https://www.blockchain.com/explorer/addresses/btc/{address}'
        webbrowser.open(url)

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
        self.total_steps = end - start
        self.scanning = True
        if self.random_button.isChecked():
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        elif self.sequence_button.isChecked():
            self.current = start
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_sequence(key_format,start, end))
        elif self.reverse_button.isChecked():
            self.current = end
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_reverse(key_format, start, end))
        self.timer.start()
        self.start_time = time.time()
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
            key = Key.from_int(dec)
            wif = bytes_to_wif(key.to_bytes(), compressed=False)
            wif1 = bytes_to_wif(key.to_bytes(), compressed=True)
            key1 = Key(wif)
            caddr = key.address
            uaddr = key1.address
            if caddr in addfind:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                self.winner_Result(caddr, dec, HEX)
            if uaddr in addfind:
                found +=1
                self.found_keys_scanned_edit.setText(str(found))
                self.winner_Result(uaddr, dec, HEX)

            startPrivKey+=1
        self.value_edit_dec.setText(str(dec))
        self.value_edit_hex.setText(HEX)
        self.uncompressed_address_edit.setText(uaddr)
        self.compressed_address_edit.setText(caddr)
        if self.sequence_button.isChecked():
            with open('start_scanned_key.txt', 'w') as f:
                f.write(str(HEX))
        elif self.reverse_button.isChecked():
            with open('end_scanned_key.txt', 'w') as f:
                f.write(str(HEX))
    def winner_Result(self, addr, dec, HEX):
        message = f'\nWINNER Nice One !!!\n{addr}\nDecimal Private Key\n{dec}\nHexadecimal Private Key\n{HEX}\n'
        with open("Winner.txt", "a") as f:
            f.write(message)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Result")
        msg_box.setText(message)
        msg_box.addButton(QMessageBox.Ok)
        msg_box.exec_()
        
    def update_display(self, start, end):
        total_steps = end - start
        max_value = 10000
        if not self.scanning:
            self.timer.stop()
            return
        self.num = random.randint(start, end)
        scaled_current_step = int((self.num - start) * max_value / total_steps)
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(scaled_current_step)
        self.generate_crypto()
        self.counter += self.power_format

    def update_display_sequence(self, key_format, start, end):
        total_steps = end - start
        self.num = self.current
        max_value = 10000
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
        scaled_current_step = int((self.num - start) * max_value / total_steps)
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(scaled_current_step)
        self.generate_crypto()
        self.current += self.power_format
        self.counter += self.power_format

    def update_display_reverse(self, key_format, start, end):
        total_steps = end - start
        self.num = self.current
        max_value = 10000
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
        scaled_current_step = int((self.num - start) * max_value / total_steps)
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(scaled_current_step)
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
    processes = []
    for i in range(3):
        process = multiprocessing.Process(target=run_app)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()