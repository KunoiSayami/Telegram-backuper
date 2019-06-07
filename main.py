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
from pyrogram import Client, Message
from libpy3.Encrypt import encrypt_by_AES_GCM as AES_GCM
import sys
from configparser import ConfigParser
import gzip
import shutil
import os
import traceback
import logging
import time

logger = logging.getLogger('telegram-backuper')

config = ConfigParser()
config.read('config.ini')
app = Client(
	session_name='session',
	api_id=config['account']['api_id'],
	api_hash=config['account']['api_hash'],
	app_version='tgbackuper',
	no_updates = True
)

class delay_update(object):
	def __init__(self, msg: Message):
		self.msg = msg
		self.last_send = 0

	def update_process(self, _: Client, size: int, total_size: int):
		print('Progress: %.2f%%'%((size/total_size)*100), end = '\r')
		if time.time() - self.last_send > 5:
			self.msg.edit('Progress: %.2f%%'%((size/total_size)*100))
			self.last_send = time.time()

def encrypt(file_name: str):
	logger.info('Gzipping file')
	with open(file_name, 'rb') as fin, gzip.open('.tmp.gz', 'wb') as gout:
		shutil.copyfileobj(fin, gout)
	logger.info('Encrypting file')
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
		dl = delay_update(app.send_message('me', 'Backup start'))
		if config['encrypt']['switch']:
			encrypt(file_name)
			logger.info('Sending file')
			r = app.send_document('me', '{}.encrypt'.format(file_name), progress = dl.update_process)
		else:
			r = app.send_document('me', '{}'.format(file_name), progress = dl.update_process)
		if not config.has_section('backup'):
			config.add_section('backup')
		config['backup']['file_id'] = r.document.file_id
		config['backup']['msg_id'] = str(r.message_id)
		logger.info('Backup completed!')
		dl.msg.delete()
		with open('config.ini', 'w') as fin: config.write(fin)
		if msg_id != '': app.delete_messages('me', msg_id)
		if config['backup']['delete_after_upload']:
			os.remove(file_name)
			if config['encrypt']['switch']:
				os.remove(f'{file_name}.encrypt')
		logger.info('Backup %s successfully', r.document.file_id)
	except:
		logger.debug(traceback.format_exc())
	finally:
		app.stop()

def download_file():
	try:
		app.download_media(config['backup']['file_id'], 'download_file')
		os.rename('downloads/download_file', 'download_file')
		if config['encrypt']['switch']:
			decrypt('download_file')
		Log.info('Download {} successfully', config['backup']['file_id'])
	except:
		logger.debug(traceback.format_exc())
	finally:
		app.stop()

if __name__ == "__main__":
	logging.getLogger("pyrogram").setLevel(logging.WARNING)
	logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s')
	if len(sys.argv) == 1:
		app.start()
		upload_file(config['backup']['filename'])
	elif len(sys.argv) == 2:
		app.start()
		if sys.argv[1] == 'download':
			if config.has_option('backup', 'file_id'):
				download_file()
			else:
				logger.error('file_id not found')
				app.stop()
		elif sys.argv[1] == 'login':
			app.stop()
		else:
			upload_file(sys.argv[1])
	else:
		print('''usage:
	<program name>:				dircet upload file name which setting in configure file to telegram server
	<program name> login:    	to login Telegram account
	<program name> download:    to download uploaded file
	<program name> <file name>: upload file to telegram server
		''')


