# Copyright (c) 2010, 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Read / Write an OOPS dict as an rfc822 formatted message.

This style of OOPS format is very web server specific, not extensible - it
should be considered deprecated.

The reports this serializer handles always have the following variables (See
the python-oops api docs for more information about these variables):

* id: The name of this error report.
* type: The type of the exception that occurred.
* value: The value of the exception that occurred.
* time: The time at which the exception occurred.
* reporter: The reporting program.
* topic: The identifier for the template/script that oopsed.
  [this is written as Page-Id for compatibility with as yet unported tools.]
* branch_nick: The branch nickname.
* revno: The revision number of the branch.
* tb_text: A text version of the traceback.
* username: The user associated with the request.
* url: The URL for the failed request.
* req_vars: The request variables. Either a list of 2-tuples or a dict.
* branch_nick: A name for the branch of code that was running when the report
  was triggered.
* revno: The revision that the branch was at.
* Informational: A flag, True if the error wasn't fatal- if it was
  'informational'.
  [Deprecated - this is no longer part of the oops report conventions. Existing
   reports with it set are still read, but the key is only present if it was
   truely in the report.]
"""


__all__ = [
    'read',
    'write',
    ]

__metaclass__ = type

import datetime
import logging
import rfc822
import re
import urllib

import iso8601


def read(fp):
    """Deserialize an OOPS from an RFC822 format message."""
    msg = rfc822.Message(fp)
    id = msg.getheader('oops-id')
    exc_type = msg.getheader('exception-type')
    exc_value = msg.getheader('exception-value')
    datestr = msg.getheader('date')
    if datestr is not None:
        date = iso8601.parse_date(msg.getheader('date'))
    else:
        date = None
    topic = msg.getheader('topic')
    if topic is None:
        topic = msg.getheader('page-id')
    username = msg.getheader('user')
    url = msg.getheader('url')
    try:
        duration = float(msg.getheader('duration', '-1'))
    except ValueError:
        duration = float(-1)
    informational = msg.getheader('informational')
    branch_nick = msg.getheader('branch')
    revno = msg.getheader('revision')
    reporter = msg.getheader('oops-reporter')

    # Explicitly use an iterator so we can process the file
    # sequentially. In most instances the iterator will actually
    # be the file object passed in because file objects should
    # support iteration.
    lines = iter(msg.fp)

    statement_pat = re.compile(r'^(\d+)-(\d+)(?:@([\w-]+))?\s+(.*)')

    def is_req_var(line):
        return "=" in line and not statement_pat.match(line)

    def is_traceback(line):
        return line.lower().startswith('traceback') or line.startswith(
            '== EXTRA DATA ==')

    req_vars = []
    statements = []
    first_tb_line = ''
    for line in lines:
        first_tb_line = line
        line = line.strip()
        if line == '':
            continue
        else:
            match = statement_pat.match(line)
            if match is not None:
                start, end, db_id, statement = match.groups()
                if db_id is not None:
                    db_id = intern(db_id)  # This string is repeated lots.
                statements.append(
                    [int(start), int(end), db_id, statement])
            elif is_req_var(line):
                key, value = line.split('=', 1)
                req_vars.append([urllib.unquote(key), urllib.unquote(value)])
            elif is_traceback(line):
                break
    req_vars = dict(req_vars)

    # The rest is traceback.
    tb_text = ''.join([first_tb_line] + list(lines))

    result = dict(id=id, type=exc_type, value=exc_value, time=date,
            topic=topic, tb_text=tb_text, username=username, url=url,
            duration=duration, req_vars=req_vars, timeline=statements,
            branch_nick=branch_nick, revno=revno)
    if informational is not None:
        result['informational'] = informational
    if reporter is not None:
        result['reporter'] = reporter
    return result


def _normalise_whitespace(s):
    """Normalise the whitespace in a string to spaces"""
    if s is None:
        return None # (used by the cast to %s to get 'None')
    return ' '.join(s.split())


def _safestr(obj):
    if isinstance(obj, unicode):
        return obj.replace('\\', '\\\\').encode('ASCII',
                                                'backslashreplace')
    # A call to str(obj) could raise anything at all.
    # We'll ignore these errors, and print something
    # useful instead, but also log the error.
    # We disable the pylint warning for the blank except.
    try:
        value = str(obj)
    except:
        logging.getLogger('oops_datedir_repo.serializer_rfc822').exception(
            'Error while getting a str '
            'representation of an object')
        value = '<unprintable %s object>' % (
            str(type(obj).__name__))
    # Some str() calls return unicode objects.
    if isinstance(value, unicode):
        return _safestr(value)
    # encode non-ASCII characters
    value = value.replace('\\', '\\\\')
    value = re.sub(r'[\x80-\xff]',
                   lambda match: '\\x%02x' % ord(match.group(0)), value)
    return value


def to_chunks(report):
    """Returns a list of bytestrings making up the serialized oops."""
    chunks = []
    def header(label, key, optional=True):
        if optional and key not in report:
            return
        value = _safestr(report[key])
        value = _normalise_whitespace(value)
        chunks.append('%s: %s\n' % (label, value))
    header('Oops-Id', 'id', optional=False)
    header('Exception-Type', 'type')
    header('Exception-Value', 'value')
    if 'time' in report:
        chunks.append('Date: %s\n' % report['time'].isoformat())
    header('Page-Id', 'topic')
    header('Branch', 'branch_nick')
    header('Revision', 'revno')
    header('User', 'username')
    header('URL', 'url')
    header('Duration', 'duration')
    header('Informational', 'informational')
    header('Oops-Reporter', 'reporter')
    chunks.append('\n')
    safe_chars = ';/\\?:@&+$, ()*!'
    if 'req_vars' in report:
        try:
            items = sorted(report['req_vars'].items())
        except AttributeError:
            items = report['req_vars']
        for key, value in items:
            chunks.append('%s=%s\n' % (
                    urllib.quote(_safestr(key), safe_chars),
                    urllib.quote(_safestr(value), safe_chars)))
        chunks.append('\n')
    if 'timeline' in report:
        for row in report['timeline']:
            (start, end, category, statement) = row[:4]
            chunks.append('%05d-%05d@%s %s\n' % (
                start, end, _safestr(category),
                _safestr(_normalise_whitespace(statement))))
        chunks.append('\n')
    if 'tb_text' in report:
        chunks.append(_safestr(report['tb_text']))
    return chunks


def write(report, output):
    """Write a report to a file."""
    output.writelines(to_chunks(report))
