import sys
import random
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from bloomfilter import BloomFilter, ScalableBloomFilter, SizeGrowthRate
import secp256k1 as ice
import time
import locale
import qdarktheme

locale.setlocale(locale.LC_ALL, '')

mizogg = f'''
 Made by Mizogg Version LAST FOR NOW 😥  © mizogg.co.uk 2018 - 2023   {f"[>] Running with Python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}"}
'''
try:
    with open('btc.bf', "rb") as fp:
        addfind = BloomFilter.load(fp)
except FileNotFoundError:

    filename = 'btc.txt'
    with open(filename) as file:
        addfind = file.read().split()

with open('eth.bf', "rb") as fp:
    bloom_filtereth = BloomFilter.load(fp)
    
app = QApplication(sys.argv)

# Apply dark theme.
qdarktheme.setup_theme()

class KnightRiderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.position = 0
        self.direction = 1
        self.lightWidth = 35
        self.lightHeight = 12
        self.lightSpacing = 10
        self.lightColor = QColor(173, 216, 230)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def startAnimation(self):
        self.timer.start(5)

    def stopAnimation(self):
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(12):
            lightX = self.position + i * (self.lightWidth + self.lightSpacing)
            lightRect = QRect(lightX, 0, self.lightWidth, self.lightHeight)
            painter.setBrush(self.lightColor)
            painter.drawRoundedRect(lightRect, 5, 5)

    def update(self):
        self.position += self.direction
        if self.position <= 0 or self.position >= self.width() - self.lightWidth - self.lightSpacing:
            self.direction *= -1
        self.repaint()
        
class CustomProgressBar(QProgressBar):
    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        progress_str = f"Progress: {self.value() / self.maximum() * 100:.5f}%"
        painter.setPen(QColor("white"))

        font = QFont("Courier", 10)
        font.setBold(True)
        painter.setFont(font)

        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, progress_str)
        
class WinnerDialog(QDialog):
    def __init__(self, WINTEXT, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QTMizICE_Display.py  WINNER")
        layout = QVBoxLayout(self)
        title_label = QLabel("!!!! 🎉 🥳CONGRATULATIONS🥳 🎉 !!!!")
        layout.addWidget(title_label)
        informative_label = QLabel("© MIZOGG 2018 - 2023")
        layout.addWidget(informative_label)
        detail_label = QPlainTextEdit(WINTEXT)
        layout.addWidget(detail_label)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        self.setMinimumSize(640, 440) 
    
class GUIInstance(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(80, 80, 1400, 560)
        
        self.initUI()

    def initUI(self):
        # 000000000000000000000000000000000000000000000001a838b13505b26867
        font = QFont()
        font.setPointSize(14)  
        self.setWindowTitle('Hunter QT with Mizogg ICE Version')
        title_label = QLabel('<html><center><font size="8"> 🌟Hunter QT with Mizogg Keys Full🌟 </font></center></html>')
        title_label.setStyleSheet("QLabel { color: lightgray; }")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label1 = QLabel('<html><center><font size="5">❤️ Good Luck and Happy Hunting MIzogg ❤️</font></center></html>')
        title_label1.setStyleSheet("QLabel { color: lightgray; }")
        title_label1.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
        display_label = QLabel('How Many to Display?')
        radio_button_layout.addWidget(display_label)

        self.format_combo_box_POWER = QComboBox()
        self.format_combo_box_POWER.addItem("1")
        self.format_combo_box_POWER.addItem("128")
        self.format_combo_box_POWER.addItem("256")
        self.format_combo_box_POWER.addItem("512")
        self.format_combo_box_POWER.addItem("1024")
        self.format_combo_box_POWER.addItem("2048")
        self.format_combo_box_POWER.addItem("4096")
        self.format_combo_box_POWER.addItem("8192")
        radio_button_layout.addWidget(self.format_combo_box_POWER)

        start_button = QPushButton('Start')
        start_button.setStyleSheet("color: white; background-color: green")
        start_button.clicked.connect(self.start)

        stop_button = QPushButton('Stop')
        stop_button.setStyleSheet("color: white; background-color: red")
        stop_button.clicked.connect(self.stop)

        radio_button_layout.addWidget(start_button)
        radio_button_layout.addWidget(stop_button)

        start_label = QLabel('Start Hexadecimal Decimal or Bit value:')
        start_label.setStyleSheet("color: green")
        self.start_edit = QLineEdit('1')
        self.start_edit.setStyleSheet("color: green")

        end_label = QLabel('End Hexadecimal Decimal or Bit value :')
        end_label.setStyleSheet("color: green")
        self.end_edit = QLineEdit('115792089237316195423570985008687907852837564279074904382605163141518161494336')
        self.end_edit.setStyleSheet("color: green")

        dec_label = QLabel(' Dec value :')
        self.value_edit_dec = QLineEdit()
        self.value_edit_dec.setReadOnly(True)

        hex_label = QLabel(' HEX value :')
        self.value_edit_hex = QLineEdit()
        self.value_edit_hex.setReadOnly(True)
        current_scan_layout = QHBoxLayout()
        
        current_scan_layout.addWidget(dec_label)
        current_scan_layout.addWidget(self.value_edit_dec)
        current_scan_layout.addWidget(hex_label)
        current_scan_layout.addWidget(self.value_edit_hex)

        # Create checkboxes for each address format
        self.compressed_checkbox = QCheckBox("Compressed")
        self.uncompressed_checkbox = QCheckBox("Uncompressed")
        self.p2sh_checkbox = QCheckBox("P2SH")
        self.bech32_checkbox = QCheckBox("Bech32")
        self.eth_checkbox = QCheckBox("ETH")
        
        # Set the checkboxes to start checked
        self.compressed_checkbox.setChecked(True)
        self.uncompressed_checkbox.setChecked(True)
        self.p2sh_checkbox.setChecked(True)
        self.bech32_checkbox.setChecked(True)
        self.eth_checkbox.setChecked(True)


        # Adjust the font size of the text
        font = self.compressed_checkbox.font()
        font.setPointSize(14)  # Adjust this size as needed
        self.compressed_checkbox.setFont(font)
        self.uncompressed_checkbox.setFont(font)
        self.p2sh_checkbox.setFont(font)
        self.bech32_checkbox.setFont(font)
        self.eth_checkbox.setFont(font)
         # Create a QHBoxLayout for the Address Type checkboxes
        address_type_layout = QHBoxLayout()
        address_type_layout.addWidget(self.compressed_checkbox)
        address_type_layout.addWidget(self.uncompressed_checkbox)
        address_type_layout.addWidget(self.p2sh_checkbox)
        address_type_layout.addWidget(self.bech32_checkbox)
        address_type_layout.addWidget(self.eth_checkbox)


        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(title_label1)
        layout.addLayout(radio_button_layout)
        
        layout.addLayout(address_type_layout)
        
        layout.addWidget(start_label)
        layout.addWidget(self.start_edit)
        layout.addWidget(end_label)
        layout.addWidget(self.end_edit)
        layout.addLayout(current_scan_layout)

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

        progress_layout_text = QHBoxLayout()
        progress_label = QLabel('progress %')
        self.progress_bar = CustomProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        progress_layout_text.addWidget(progress_label)
        progress_layout_text.addWidget(self.progress_bar)
        layout.addLayout(progress_layout_text)
        self.address_layout_ = QGridLayout()
        self.priv_label = QLabel("DEC Keys: ")
        self.priv_text = QTextEdit(self)
        self.HEX_label = QLabel("HEX Keys: ")
        self.HEX_text = QTextEdit(self)
        self.uncomp_label = QLabel("Uncompressed Address: ")
        self.uncomp_text = QTextEdit(self)
        self.comp_label = QLabel("Compressed Address: ")
        self.comp_text = QTextEdit(self)
        self.p2sh_label = QLabel("p2sh Address: ")
        self.p2sh_text = QTextEdit(self)
        self.bech32_label = QLabel("bech32 Address: ")
        self.bech32_text = QTextEdit(self)
        self.ethaddr_label = QLabel("ETH Address: ")
        self.ethaddr_text = QTextEdit(self)
        self.address_layout_.addWidget(self.priv_label, 1, 0)
        self.address_layout_.addWidget(self.priv_text, 2, 0)
        self.address_layout_.addWidget(self.HEX_label, 1, 1)
        self.address_layout_.addWidget(self.HEX_text, 2, 1)
        self.address_layout_.addWidget(self.uncomp_label, 1, 2)
        self.address_layout_.addWidget(self.uncomp_text, 2, 2)
        self.address_layout_.addWidget(self.comp_label, 1, 3)
        self.address_layout_.addWidget(self.comp_text, 2, 3)
        self.address_layout_.addWidget(self.p2sh_label, 1, 4)
        self.address_layout_.addWidget(self.p2sh_text, 2, 4)
        self.address_layout_.addWidget(self.bech32_label, 1, 5)
        self.address_layout_.addWidget(self.bech32_text, 2, 5)
        self.address_layout_.addWidget(self.ethaddr_label, 1, 6)
        self.address_layout_.addWidget(self.ethaddr_text, 2, 6)
        layout.addLayout(self.address_layout_)
        
        self.knightRiderWidget = KnightRiderWidget(self)
        self.knightRiderWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.knightRiderWidget.setMinimumHeight(20)
        
        self.knightRiderLayout = QHBoxLayout()
        self.knightRiderLayout.setContentsMargins(10, 15, 10, 10)
        self.knightRiderLayout.addWidget(self.knightRiderWidget)

        self.knightRiderGroupBox = QGroupBox(self)
        self.knightRiderGroupBox.setTitle("Running Process ")
        self.knightRiderGroupBox.setFont(font)
        self.knightRiderGroupBox.setStyleSheet("QGroupBox { border: 5px solid lightblue; padding: 2px; }")
        self.knightRiderGroupBox.setLayout(self.knightRiderLayout)
        mizogg_label = QLabel(mizogg, self)
        mizogg_label.setStyleSheet("font-size: 18px; font-weight: bold; color: lightblue;")
        mizogg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.knightRiderGroupBox)
        layout.addWidget(mizogg_label)
        self.setLayout(layout)
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
        self.total_steps = end - start
        self.scanning = True
        if self.random_button.isChecked():
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display(start, end))
        elif self.sequence_button.isChecked():
            self.current = start
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_sequence(key_format, start, end))
        elif self.reverse_button.isChecked():
            self.current = end
            self.timer = QTimer(self)
            self.timer.timeout.connect(lambda: self.update_display_reverse(key_format, start, end))
        self.timer.start()
        self.start_time = time.time()
        self.timer.timeout.connect(self.update_keys_per_sec)
        self.knightRiderWidget.startAnimation()

    def stop(self):
        self.timer.stop()
        self.worker_finished('Recovery Finished')
    
    def worker_finished(self, result):
        if self.scanning:
            QMessageBox.information(self, 'Recovery Finished', result)
        self.scanning = False
        self.knightRiderWidget.stopAnimation()

    def generate_crypto(self):
        dec_keys = []
        HEX_keys = []
        uncomp_keys = []
        comp_keys = []
        p2sh_keys = []
        bech32_keys = []
        ethaddr_keys = []
        found = int(self.found_keys_scanned_edit.text())
        startPrivKey = self.num

        for i in range(0, self.power_format):
            dec = int(startPrivKey)
            HEX = "%064x" % dec
            dec_keys.append(dec)
            HEX_keys.append(HEX)
            if self.compressed_checkbox.isChecked():
                caddr = ice.privatekey_to_address(0, True, dec)
                
                if caddr in addfind:
                    found += 1
                    self.found_keys_scanned_edit.setText(str(found))
                    WINTEXT = f'\n {caddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
                    print(WINTEXT)
                    with open("foundcaddr.txt", "a") as f:
                        f.write(WINTEXT)
                    winner_dialog = WinnerDialog(WINTEXT, self)
                    winner_dialog.exec()

                comp_keys.append(caddr)
            
            if self.uncompressed_checkbox.isChecked():
                uaddr = ice.privatekey_to_address(0, False, dec)
                if uaddr in addfind:
                    found += 1
                    self.found_keys_scanned_edit.setText(str(found))
                    WINTEXT = f'\n {uaddr} \n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX}  \n'
                    print(WINTEXT)
                    with open("founduaddr.txt", "a") as f:
                        f.write(WINTEXT)
                    winner_dialog = WinnerDialog(WINTEXT, self)
                    winner_dialog.exec()

                uncomp_keys.append(uaddr)
            
            if self.p2sh_checkbox.isChecked():
                p2sh = ice.privatekey_to_address(1, True, dec)
                if p2sh in addfind:
                    found += 1
                    self.found_keys_scanned_edit.setText(str(found))
                    WINTEXT = f'\n {p2sh}\nDecimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                    print(WINTEXT)
                    with open("foundp2sh.txt", "a") as f:
                        f.write(WINTEXT)
                    winner_dialog = WinnerDialog(WINTEXT, self)
                    winner_dialog.exec()

                p2sh_keys.append(p2sh)
            
            if self.bech32_checkbox.isChecked():
                bech32 = ice.privatekey_to_address(2, True, dec)
                if bech32 in addfind:
                    found += 1
                    self.found_keys_scanned_edit.setText(str(found))
                    WINTEXT = f'\n {bech32}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                    print(WINTEXT)
                    with open("foundbech32.txt", "a") as f:
                        f.write(WINTEXT)
                    winner_dialog = WinnerDialog(WINTEXT, self)
                    winner_dialog.exec()

                bech32_keys.append(bech32)
            if self.eth_checkbox.isChecked():
                ethaddr = ice.privatekey_to_ETH_address(dec)
                
                if ethaddr[2:] in bloom_filtereth:
                    found += 1
                    self.found_keys_scanned_edit.setText(str(found))
                    WINTEXT = f'\n {ethaddr}\n Decimal Private Key \n {dec} \n Hexadecimal Private Key \n {HEX} \n'
                    print(WINTEXT)
                    with open("foundeth.txt", "a") as f:
                        f.write(WINTEXT)
                    winner_dialog = WinnerDialog(WINTEXT, self)
                    winner_dialog.exec()

                ethaddr_keys.append(ethaddr)
            startPrivKey += 1
        
        self.value_edit_dec.setText(str(dec))
        self.value_edit_hex.setText(HEX)
        self.priv_text.setText('\n'.join(map(str, dec_keys)))
        self.HEX_text.setText('\n'.join(HEX_keys))
        self.uncomp_text.setText('\n'.join(uncomp_keys))
        self.comp_text.setText('\n'.join(comp_keys))
        self.p2sh_text.setText('\n'.join(p2sh_keys))
        self.bech32_text.setText('\n'.join(bech32_keys))
        self.ethaddr_text.setText('\n'.join(ethaddr_keys))

        
            
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
        total_steps = end - start
        max_value = 10000
        scaled_current_step = min(max_value, max(0, int(self.num * max_value / total_steps)))
        self.progress_bar.setMaximum(max_value)
        self.progress_bar.setValue(scaled_current_step)
        self.generate_crypto()
        self.counter += self.power_format


    def update_display_sequence(self, key_format, start, end):
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
        total_steps = end - start
        current_step = self.num - start  # Calculate the current step within the range
        scaled_current_step = (current_step / total_steps) * 10000  # Calculate the scaled progress
        self.progress_bar.setMaximum(10000)
        self.progress_bar.setValue(int(scaled_current_step))
        self.generate_crypto()
        self.current += self.power_format
        self.counter += self.power_format
    
    def update_display_reverse(self, key_format, start, end):
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
        total_steps = end - start
        current_step = end - self.num  # Calculate the current step within the range in reverse
        scaled_current_step = (current_step / total_steps) * 10000  # Calculate the scaled progress
        self.progress_bar.setMaximum(10000)
        self.progress_bar.setValue(int(scaled_current_step))
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

        total_keys_scanned_text = self.total_keys_scanned_edit.text()
        total_keys_scanned = locale.atoi(total_keys_scanned_text) + self.counter

        total_keys_scanned_formatted = locale.format_string("%d", total_keys_scanned, grouping=True)
        keys_per_sec_formatted = locale.format_string("%.2f", keys_per_sec, grouping=True)

        self.total_keys_scanned_edit.setText(total_keys_scanned_formatted)
        self.keys_per_sec_edit.setText(keys_per_sec_formatted)
        self.start_time = time.time()
        self.counter = 0

if __name__ == '__main__':
    gui_instance = GUIInstance()
    gui_instance.show()
    sys.exit(app.exec())