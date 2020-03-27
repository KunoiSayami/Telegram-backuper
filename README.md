# Telegram backuper

## Compatibility tips

d818d5f78fe742db0fab066c3b9f21533e671fa1 and previous commit version is not support current encrypt method, please update to mainline version to use new feature.

## Usage

* Rename `config.ini.default` to `config.ini`
* Parse `api_hash` and `api_id` to `config.ini` obtained from [telegram](https://my.telegram.org/apps)
* Change other options in `config.ini`
* Run `backup.py` to login your telegram account, then start backup

## LICENSE

[![](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.txt)

Copyright (C) 2018-2020 KunoiSayami

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
