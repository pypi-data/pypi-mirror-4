# -*- coding: utf-8 -*-

"""
This file is part of the emailcontent Framework
Copyrighted by Karel Vedecia Ortiz <kverdecia@uci.cu, kverdecia@gmail.com>
License: LGPLv3 (http://www.gnu.org/licenses/lgpl.html)
"""
__author__ = "Karel Antonio Verdecia Ortiz"
__contact__ = "kverdecia@uci.cu"


import os
import datetime
import email
import email.message
import email.header
import email.utils
import re
import yaml
from charset import text_to_utf8
from cStringIO import StringIO


class MetaData(object):
    """
    Each instance of this class will have the metadata from an email message.
    """
    re_recieved = re.compile(r'for <(.*@.*)>;')
    re_in_reply_to = re.compile(r"<.*>", re.MULTILINE)
    
    def __init__(self, message=None):
        """
        Parameters
        ----------
        message: email.message.Message
            Email message from which the metadata will be extracted.
        """
        self.names = dict()
        if message is None:
            self.clear()
        else:
            assert isinstance(message, email.message.Message)
            self.set_message(message)

    def __getstate__(self):
        result = dict(self.__dict__)
        result['message'] = None
        return result

    def clear(self):
        """Clear the extracted metadata.
        """
        self.message = None
        self.id = None
        self.to = None
        self.sender = None
        self.reply_to = None
        self.cc = None
        self.bcc = None
        self.in_reply_to = None
        self.subject = None
        self.content_type = None
        self.date = None
        self.timestamp = None
        self.received_date = None
        self.received_timestamp = None
        self.charset = None
        self.receivers = None

    @staticmethod
    def from_message(message):
        """Creates an instance of the metadata class from an email message.
        
        Parameters
        ----------
        message: email.message.Message
            Email message from which the metadata will be extracted.
        
        Returns: emailcontent.metadata.MetaData
            Returns an object with the metadata of the message.
        """
        result = MetaData()
        result.set_message(message)
        return result

    def set_message(self, message):
        """
        :param message: Correo del que se van a extraer los metadatos.
        :type message: `email.message.Message`
        """
        assert isinstance(message, email.message.Message)
        self.message = message
        self.id = message['Message-ID']
        self.to = self._address('To')
        senders = self._address('From')
        self.sender = senders[0] if senders else None
        addresses = self._address('Reply-To')
        self.reply_to = addresses[0] if addresses else None
        self.cc = self._address('Cc')
        self.bcc = self._address('Bcc')
        in_replay_to = message['In-Reply-To']
        if in_replay_to:
            items = self.re_in_reply_to.findall(in_replay_to)
            in_replay_to = items[0] if items else in_replay_to
        self.in_reply_to = in_replay_to
        self.subject = self._header_str('Subject')
        self.content_type = message.get_content_type()
        self.date = self._date('Date')
        self.timestamp = self._timestamp('Date')
        self.received_date = self._date('Received-Date')
        self.received_timestamp = self._timestamp('Received-Date')
        self.charset = message.get_charset()
        self.receivers = self._receivers()

    def to_string(self):
        """Returns a string representation with the metadata.
        """
        f = StringIO()
        print >> f, "id:", self.id
        print >> f, "to:", self._address_str('To')
        print >> f, "from:", self._address_str('From')
        print >> f, "reply-to:", self._address_str('Reply-To')
        print >> f, "in-reply-to:", self.in_reply_to
        print >> f, "cc:", self._address_str('Cc')
        print >> f, "bcc:", self._address_str('Bcc')
        print >> f, "subject:", self._header_str('Subject')
        print >> f, "date:", self._date_str('Date')
        print >> f, "timestamp:", self._timestamp_str('Date')
        print >> f, "received-date:", self._date_str('Received-Date')
        print >> f, "received-timestamp:", self._timestamp_str('Received-Date')
        print >> f, "content-type:", self.content_type or ""
        return f.getvalue()

    def to_yaml(self):
        """Returns a yaml formated string with the message metadata.
        """
        data = dict(id=self.id,
            in_reply_to=self.message['In-Reply-To'],
            recipient=self._address_str('To'),
            sender=self._address_str('From'),
            reply_to=self._address_str('Reply-To'),
            cc=self._address_str('Cc'))
        return yaml.dump(data)

    def _get_header(self, header_name):
        items = email.header.decode_header(self.message[header_name])
        values = []
        for s, enc in items:
            try:
                values.append(s.decode(enc or 'ascii'))
            except UnicodeDecodeError:
                try:
                    values.append(text_to_utf8(s))
                except UnicodeDecodeError:
                    continue
        return ' '.join(values).encode('utf-8')

    def _header_values(self, header_name):
        header = self.message[header_name]
        if header is None:
            return []
        items = email.header.decode_header(header)
        values = []
        for s, enc in items:
            try:
                values.append(s.decode(enc or 'ascii'))
            except UnicodeDecodeError:
                try:
                    values.append(text_to_utf8(s))
                except UnicodeDecodeError:
                    continue
        try:
            return [val.encode('utf-8') for val in values]
        except UnicodeDecodeError:
            return values

    def _header_str(self, header_name, join_str=' '):
        return join_str.join(self._header_values(header_name))
    
    def _address(self, header_name):
        def decode(text, encoding):
            if encoding is None:
                return text
            try:
                return text.decode(encoding)
            except UnicodeDecodeError:
                return text
        def encode(text):
            try:
                return text.encode('utf-8')
            except UnicodeEncodeError:
                return text
        result = dict()
        header_value = self.message[header_name]
        if not header_value:
            return []
        result = dict()
        header_value = header_value.replace('\n', ' ')
        pieces = email.header.decode_header(header_value)
        pieces = [(text.decode(encoding) if encoding else text) for text, encoding in pieces]
        header_value = u"".join(pieces).strip()
        name, address = email.utils.parseaddr(header_value)
        while address:
            result[address] = name or None
            index = header_value.find(address) + len(address)
            if index >= len(header_value):
                break
            if header_value[index] == '>':
                index += 1
            if index >= len(header_value):
                break
            if header_value[index] == ',':
                index += 1
            header_value = header_value[index:].strip()
            name, address = email.utils.parseaddr(header_value)
        self.names.update(result)
        addresses = [encode(address) for address in result.keys()]
        return sorted(addresses)

    def _address_str(self, header_name, join_str=', '):
        return join_str.join(self._address(header_name))

    def _timestamp(self, header_name):
        header = self.message[header_name]
        if header is None:
            return None
        data = email.utils.parsedate_tz(header)
        if data is None:
            return None
        return email.utils.mktime_tz(data)

    def _timestamp_str(self, header_name):
        timestamp = self._timestamp(header_name)
        if timestamp is None:
            return ""
        return str(timestamp)

    def _date(self, header_name):
        stamp = self._timestamp(header_name)
        if stamp is None or stamp == 'None':
            return None
        date = datetime.datetime.fromtimestamp(stamp)
        return date

    def _date_str(self, header_name):
        date = self._date(header_name)
        if date is None:
            return ""
        return date.strftime('%Y-%m-%d %H:%M:%S')

    def _receivers(self):
        """Devuelve un conjunto con las direcciones de correo de los receptores
        del mensaje.
        """
        result = set()
        if self.to: result.update(set(self.to))
        if self.cc : result.update(set(self.cc))
        if self.bcc: result.update(set(self.bcc))
        received = self.message.get_all('Received')
        if received:
            headers = '\r\n'.join(received)
            new = set(self.re_recieved.findall(headers))
            result.update(new)
        return result

    def addresses(self):
        """
        Devuelve un conjunto con las direcciones de correo detectadas en el
        mensaje.
        """
        result = set()
        if self.sender: result.update(set([self.sender]))
        if self.reply_to: result.update(set(self.reply_to))
        result.update(self.receivers())
        return result

    @classmethod
    def open(cls, email):
        """Abre el correo que se pasa por parámetro.

        :param email: Correo que se va a abrir. Puede ser una cadena con
            el camino en el disco, o con el contenido del correo; o un
            `stream`.
        :return: Devuelve un correo con la representación del correo que
            se pasó por parámetro.
        :rtype: `email.Email`
        :raise ValueError: Si el valor que se pasó por parámetro no es
            un correo válido.
        """
        if isinstance(email, email.message.Message):
            return email
        if isinstance(email, basestring):
            try:
                if os.path.isfile(email):
                    return email.message_from_file(open(email))
            except:
                return email.message_from_string(email)
        else:
            return email.message_from_file(email)

