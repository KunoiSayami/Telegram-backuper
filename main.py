#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# main.py
# Copyright (C) 2018 Too-Naive
#
# This module is part of Telegram-backuper and is released under
# the AGPL v3 License: https://www.gnu.org/licenses/agpl-3.0.txt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from pyrogram import Client
from libpy3.Encrypt import encrypt_by_AES_GCM as AES_GCM
from libpy3 import Log
import sys
from configparser import ConfigParser
from io import BufferedReader, BufferedWriter
import gzip
import shutil
import os
import traceback

config = ConfigParser()
config.read('config.ini')
app = Client(session_name='session',
	api_id=config['account']['api_id'],
	api_hash=config['account']['api_hash'],
	app_version='tgbackuper')

def encrypt(file_name: str):
	with open(file_name, 'rb') as fin, gzip.open('.tmp.gz', 'wb') as gout:
		shutil.copyfileobj(fin, gout)
	with open('.tmp.gz', 'rb') as fin, open('{}.encrypt'.format(file_name), 'w') as fout:
		fout.write(AES_GCM().b64encrypt(fin.read()))
	os.remove('.tmp.gz')

def decrypt(file_name: str):
	with open(file_name, 'r') as fin, open('.tmp.gz', 'wb') as fout:
		fout.write(AES_GCM().b64decrypt(fin.read()))
	with gzip.open('.tmp.gz', 'rb') as gin, open('{}.origin'.format(file_name), 'wb') as fout:
		shutil.copyfileobj(gin, fout)
	os.remove('.tmp.gz')

def upload_file(file_name: str):
	try:
		msg_id = int(config['backup']['msg_id']) if config.has_option('backup', 'msg_id') and config['backup']['msg_id'] != '' else ''
		encrypt(file_name)
		r = app.send_document('me', '{}.encrypt'.format(file_name))
		config['backup']['file_id'] = r.document.file_id
		config['backup']['msg_id'] = str(r.message_id)
		with open('config.ini', 'w') as fin: config.write(fin)
		if msg_id != '': app.delete_messages('me', msg_id)
		Log.info('Backup {} successfully', r.document.file_id)
	except:
		Log.exc()
	finally:
		app.stop()

def download_file():
	try:
		app.download_media(config['backup']['file_id'], 'download_file')
		os.rename('downloads/download_file', 'download_file')
		decrypt('download_file')
		Log.info('Download {} successfully', config['backup']['file_id'])
	except:
		Log.exc()
	finally:
		app.stop()

if __name__ == "__main__":
	if len(sys.argv) == 1:
		app.start()
		upload_file(config['backup']['filename'])
	elif len(sys.argv) == 2:
		app.start()
		if sys.argv[1] == 'download':
			if config.has_option('backup', 'file_id'):
				download_file()
			else:
				print('file_id not found', file = sys.stderr)
				app.stop()
		else:
			upload_file(sys.argv[1])
	else:
		print('''usage:
	<program name> :			dircet upload file name which setting in configure file to telegram server
	<program name> download:    to download uploaded file
	<program name> <file name>: upload file to telegram server
		''')


