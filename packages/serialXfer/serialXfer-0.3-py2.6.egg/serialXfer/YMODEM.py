from XMODEM import *


'''
YMODEM Batch Transmission Session (1 file)
------------------------------------------

::

SENDER                                      RECEIVER
<-- C (command:rb)
SOH 00 FF foo.c NUL[123] CRC CRC        -->
<-- ACK
<-- C
SOH 01 FE Data[128] CRC CRC             -->
<-- ACK
SOH 02 FC Data[128] CRC CRC             -->
<-- ACK
SOH 03 FB Data[100] CPMEOF[28] CRC CRC  -->
<-- ACK
EOT                                     -->
<-- NAK
EOT                                     -->
<-- ACK
<-- C
SOH 00 FF NUL[128] CRC CRC              -->
<-- ACK

'''

class YMODEM(XMODEM):
  
  def __init__(self, *args,**kw):
    self.filename = ""
    self.meta = ""
    super(YMODEM,self).__init__(*args,**kw)
  
  def _send(self, stream, retry=16, timeout=60, quiet=0):
    '''
    Send a stream via the YMODEM protocol.
    
    >>> stream = file('/etc/issue', 'rb')
    >>> print modem.send(stream)
    True
    
    Returns ``True`` upon succesful transmission or ``False`` in case of
    failure.
    '''
    
    # initialize protocol
    error_count = 0
    cancel = 0
    while True:
      char = self.getc(1)
      if char:
        if char == CRC:
          break
        if char == CAN:
          if not quiet:
            print >> sys.stderr, 'received CAN'
          # end if
          if cancel:
            self.retval = False
            return False
          else:
            cancel = 1
          # end if
        else:
          self.log.error('send ERROR expected CRC, got %s' % (ord(char),))
        # end if
      # end if
      
      error_count += 1
      if error_count >= retry:
        self.abort(timeout=timeout)
        self.retval = False
        return False
      # end if
    # end while
    
    # send data
    error_count = 0
    packet_size = 128
    sequence = 0
    while True:
      if sequence == 0:
        data = stream.name+chr(0)
        data += "%d\0" % os.stat(stream.name).st_size
        data += chr(0) * (pack_size - len(data))
      else:        
        data = stream.read(packet_size)
      # end if
      
      if not data:
        self.log.info('sending EOS')
        break
    
      data = data.ljust(packet_size, '\xff')
  
      crc = self.calc_crc(data)
      
      # emit packet
      while True:
        self.putc(SOH)
        self.putc(chr(sequence))
        self.putc(chr(0xff - sequence))
        self.putc(data)
  
        self.putc(chr(crc >> 8))
        self.putc(chr(crc & 0xff))
        
        char = self.getc(1, timeout)
        if char == ACK:
          break
  
        if char == NAK:
          error_count += 1
          if error_count >= retry:
            # excessive amounts of retransmissions requested,
            # abort transfer
            self.abort(timeout=timeout)
            self.log.warning('excessive NAKs, transfer aborted')
            self.retval = False
            return False
          
          # return to loop and resend
          continue
      
        # protocol error
        self.abort(timeout=timeout)
        self.log.error('protocol error')
        self.retval = False
        return False

      # keep track of sequence
      sequence = (sequence + 1) % 0x100
      # end while
  
    # end of transmission
    self.putc(EOT)
    self.retval = True
    return True


  def _recv(self, stream, crc_mode, retry=16, timeout=60, delay=1, quiet=0):
    '''
    Receive a stream via the YMODEM protocol.
    
       >>> stream = file('/etc/issue', 'wb')
       >>> print modem.recv(stream)
       2342
    
    Returns the number of bytes received on success or ``None`` in case of
    failure.
    '''
    
    # initiate protocol
    error_count = 0
    char = 0
    cancel = 0
    while True:
      if error_count >= retry:
        self.abort(timeout=timeout)
        self.retval = None
        return None
      elif error_count < (retry / 2):
        if not self.putc(CRC):
          time.sleep(delay)
          error_count += 1
      
      char = self.getc(1, timeout)
      if not char:
        error_count += 1
        continue
      elif char in [SOH, STX]:
        break
      elif char == CAN:
        if cancel:
          self.retval = None
          return None
        else:
          cancel = 1
      else:
        error_count += 1
    
    # read data
    error_count = 0
    expected_size = 0
    income_size = 0
    packet_size = 128
    sequence = 0
    cancel = 0
    while True:
      while True:
        if char == SOH:
          packet_size = 128
          break
        elif char == STX:
          packet_size = 1024
          break
        elif char == EOT:
          self.putc(ACK)
          if expected_size > 0 and income_size >= expected_size:
            self.retval = expected_size
            return expected_size
          else:
            self.retval = income_size
            return income_size
          # end if
        elif char == CAN:
          # cancel at two consecutive cancels
          if cancel:
            self.retval = None
            return None
          else:
            cancel = 1
          # end if
        else:
          if not quiet:
            print >> sys.stderr, 'recv ERROR expected SOH/EOT, got', ord(char)
          # end if
          error_count += 1
          if error_count >= retry:
            self.abort()
            self.retval = None
            return None
          # end if
        # end if
      # end while
      
      # read sequence
      error_count = 0
      cancel = 0
      seq1 = ord(self.getc(1))
      seq2 = 0xff - ord(self.getc(1))
      if seq1 == sequence and seq2 == sequence:
        # sequence is ok, read packet
        # packet_size + checksum
        data = self.getc(packet_size + 2)
        
        csum = (ord(data[-2]) << 8) + ord(data[-1])
        data = data[:-2]
        self.log.debug('CRC (%04x <> %04x)' % \
                      (csum, self.calc_crc(data)))
        valid = csum == self.calc_crc(data)
        
        # valid data, append chunk
        if valid:
          self.putc(ACK)
          
          if seq1 == seq2 == 0:
            self.putc(CRC)
            filename = data.split(chr(0), 1)[0]
            if len(filename)>0:
              meta = data[len(filename)+1:].split(chr(0), 1)[0]
              try:
                meta = map(int, meta.split(' '))
              except ValueError:
                pass
              
              if len(meta)>0:
                expected_size = int(meta[0])

              self.log.debug("".join(x for x in data if ord(x)>31))
              self.filename = filename
              self.meta = meta
          else:
            income_size += len(data)
            if expected_size > 0 and income_size > expected_size:
              remain_size = expected_size-income_size
            else:
              remain_size = len(data)
            stream.write(data[:remain_size])
          # end if
          sequence = (sequence + 1) % 0x100
          char = self.getc(1, timeout)
          continue
        # end if
      else:
        # consume data
        self.getc(packet_size + 2)
        self.log.debug('expecting sequence %d, got %d/%d' % (sequence, seq1, seq2))
      
      # something went wrong, request retransmission
      self.putc(NAK)
    # end while

