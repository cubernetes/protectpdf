#!/usr/bin/env python3

import os
import sys
import json
import random
from pathlib import Path
from PySide6 import QtCore, QtWidgets
from pikepdf import Pdf, Encryption

class ProtectPdfWindow(QtWidgets.QWidget):
    def __init__(self, lang_file='en.json'):
        super().__init__()

        if os.path.isfile(lang_file):
            self.lang = json.loads(open(lang_file, 'r', encoding='utf8').read())
        else:
            print(f'Error: File {lang_file} does not exist. Using default language English')
            self.lang = default_lang

        self.buttonChooseDir = QtWidgets.QPushButton(self.lang['select_dir'])
        self.buttonStartEncrypting = QtWidgets.QPushButton(self.lang['add_pwd_protection'])
        self.exitButton = QtWidgets.QPushButton(self.lang['quit'])

        self.dirText = QtWidgets.QLabel(self.lang['no_dir_selected'])
        self.infoText = QtWidgets.QLabel(self.lang['will_be_applied_to_zero'])
        self.passwordText = QtWidgets.QLabel(self.lang['pwd'])

        self.lineEditPassword = QtWidgets.QLineEdit(self)

        self.checkBoxDecrypt = QtWidgets.QCheckBox(self.lang['remove_pwd_protection_checkbox'])

        self.layout = QtWidgets.QVBoxLayout(self)
        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox3 = QtWidgets.QHBoxLayout()

        self.layout.addLayout(self.hbox1)
        self.hbox1.addWidget(self.buttonChooseDir)
        self.hbox1.addWidget(self.dirText)

        self.layout.addLayout(self.hbox2)
        self.hbox2.addWidget(self.passwordText)
        self.hbox2.addWidget(self.lineEditPassword)

        self.layout.addLayout(self.hbox3)
        self.hbox3.addWidget(self.checkBoxDecrypt)
        self.hbox3.addWidget(self.buttonStartEncrypting)

        self.layout.addWidget(self.infoText)
        self.layout.addWidget(self.exitButton)

        self.passwordText.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        self.checkBoxDecrypt.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))

        self.buttonChooseDir.clicked.connect(self.pickDirectory)
        self.buttonStartEncrypting.clicked.connect(self.protectPdfs)
        self.checkBoxDecrypt.stateChanged.connect(lambda: self.buttonStartEncrypting.setText(self.lang['remove_pwd_protection'] if self.checkBoxDecrypt.isChecked() else self.lang['add_pwd_protection']))
        self.exitButton.clicked.connect(self.close)

        self.directory = ''
        self.pdfs = []

    @QtCore.Slot()
    def pickDirectory(self):
        self.directory = str(QtWidgets.QFileDialog.getExistingDirectory(self, self.lang['select_dir']))
        self.infoText.setText(self.lang['dirs_are_being_searched'])
        self.infoText.repaint()
        self.dirText.setText(self.directory)
        self.pdfs = list(map(str, Path(self.directory).rglob('*.pdf')))
        self.infoText.setText(self.eval_lang_string(self.lang['pdfs_were_found'], locals()))

    @QtCore.Slot()
    def protectPdfs(self):
        password = self.lineEditPassword.text()
        if not password:
            print(self.lang['no_pwd_provided'])
            self.infoText.setText(self.lang['no_pwd_provided'])
            return
        self.infoText.setText('')
        for pdf_path in self.pdfs:
            if self.checkBoxDecrypt.isChecked():
                pdf = Pdf.open(pdf_path, password=password)
                pdf.save(pdf_path + '.tmp')
            else:
                pdf = Pdf.open(pdf_path)
                pdf.save(pdf_path + '.tmp', encryption=Encryption(owner=password, user=password, R=4))
            pdf.close()
            os.remove(pdf_path)
            os.rename(pdf_path + '.tmp', pdf_path)
            print(self.eval_lang_string(self.lang['pdfs_were_modified'], locals()))
            self.infoText.setText(self.eval_lang_string(self.lang['pdfs_were_modified'], locals()))
        self.infoText.setText(self.eval_lang_string(self.lang['success'], locals()))

    def eval_lang_string(self, s, env=globals() | locals()):
        return eval("f'" + s + "'", env)

default_lang = {
	"select_dir":"Select directory",
	"quit":"Quit",
	"no_dir_selected":"No directory selected",
	"will_be_applied_to_zero":"No PDFs will be modified",
    "pwd":"Password:",
	"add_pwd_protection":"Protect PDFs with password",
	"remove_pwd_protection":"Remove passwords from PDFs",
	"remove_pwd_protection_checkbox":"Remove password?",
	"pdfs_were_found":"{str(len(self.pdfs))} PDFs were found",
	"no_pwd_provided":"No password was specified",
	"dirs_are_being_searched":"Directories are being searched",
	"pdfs_were_modified":"PDF was {\"decrypted\" if self.checkBoxDecrypt.isChecked() else \"encrypted\"} ({pdf_path})",
    "success":"Success: {len(self.pdfs)} PDFs were {\"decrypted\" if self.checkBoxDecrypt.isChecked() else \"encrypted\"}"
}

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    widget = ProtectPdfWindow()
    widget.show()

    sys.exit(app.exec())
