#!/usr/bin/env python

import ais
import datetime
from pprint import pprint
import re
import sys
import Queue

def AisSplit(line):
  fields = line.split(',')
  if len(fields) == 9:
    hdr, total, line_num, seq, chan, body, checksum, station, timestamp = fields
  elif len(fields) > 9:
    hdr, total, line_num, seq, chan, body, checksum = fields[:7]
    timestamp = fields[-1]
    station = 'runknown'

  if seq: seq = int(seq)
  return {
      'hdr': hdr,
      'total': int(total),
      'line_num': int(line_num),
      'seq': int(seq) if seq else seq,
      'chan': chan,
      'body': body,
      'checksum':  checksum.split('*')[1],
      'pad': int(checksum.split('*')[0]),
      'station': station,
      'timestamp': int(timestamp),
      'raw': line.strip(),
      }

class Normalize(Queue.Queue):
  """Single station AIS normalize"""

  def __init__(self):
    self.channels = {}
    for chan in range(10):
      self.channels[chan] = []
    Queue.Queue.__init__(self)

  def put(self, line_str, line_num=None):
    line_str = line_str.strip()

    if not isinstance(line_str, str): raise TypeError('Expect single lines')

    line = AisSplit(line_str)
    seq = line['seq']

    if seq == '':
      line['raw'] = [line['raw']]  # always a list
      Queue.Queue.put(self, line)
      return

    if line['line_num'] == 1:
      self.channels[seq] = [line]
      return

    if line['line_num'] != line['total']:
      self.channels[seq].append(line)
      return

    # Complete multi line
    line['raw'] = [l['raw'] for l in self.channels[seq]] + [line['raw']]
    if len(line['raw']) != line['total']:
      self.channels[seq] = []
      return

    line['body'] = ''.join([l['body'] for l in self.channels[seq]]) + line['body']
    line['total'] = 1
    line['line_num'] = 1
    self.channels[seq] = []
    Queue.Queue.put(self, line)

for filename in sys.argv[1:]:
  q = Normalize()
  print 'tests_' + filename.replace('.', '_').replace('-','_') + ' = ['

  for line in open(filename):
    q.put(line)
    try:
      result = q.get(False)
    except Queue.Empty:
      continue
    body = result['body']
    msg_type = body[0]
    pad = result['pad']
    msg = ais.decode(body, pad)
    print '  {'
    if len(result['raw']) == 1:
      print '    \'nmea\': [ \'%s\' ],' % result['raw'][0]
    else:
      print '    \'nmea\': ['
      for raw in result['raw']:
        print '      \'%s\',' % raw
      print '    ],'
    print '    \'result\': ',
    pprint(msg)
    print '  },'
  print ']'
