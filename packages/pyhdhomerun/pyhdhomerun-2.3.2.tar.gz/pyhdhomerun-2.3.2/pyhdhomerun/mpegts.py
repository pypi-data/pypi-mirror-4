
def decode_mpegts_adaptation_data(buffer, offset):

    (length, byte1) = unpack('BB', buffer[offset:offset + 2])
    
    discontinuity         = bool(byte1 & 0b10000000)
    random_access         = bool(byte1 & 0b01000000)
    priority              = bool(byte1 & 0b00100000)
    has_pcr               = bool(byte1 & 0b00010000)
    has_opcr              = bool(byte1 & 0b00001000)
    has_splicing_point    = bool(byte1 & 0b00000100)
    has_transport_private = bool(byte1 & 0b00000010)
    has_extension         = bool(byte1 & 0b00000001)

    ptr = offset + 2
    
    if has_pcr:
        pcr = buffer[ptr:ptr + 6]
        ptr += 6
    else:
        pcr = None

    if has_opcr:
        opcr = buffer[ptr:ptr + 6]
        ptr += 6
    else:
        opcr = None

    if has_splicing_point:
        splicing_point = unpack('B', buffer[ptr])
        ptr += 1
    else:
        splicing_point = None

    return { 'DiscontinuityIndicator':            discontinuity,
             'RandomAccessIndicator':             random_access,
             'ElementaryStreamPriorityIndicator': priority,
             'PcrFlag':                           pcr,
             'OpcrFlag':                          opcr,
             'SplicingPointFlag':                 splicing_point,
             'HasTransportPrivateDataFlag':       has_transport_private,
             'HasExtension':                      has_extension,
             '_AdaptationLength':                 (1 + length)
           }

def decode_pat(buffer, offset, pointer_field, table_id, section_length):

    part_length = 5
    part = buffer[offset:offset + part_length]
    (ts_id, flags, section, last_section) = unpack('!HBBB', part)

    reserved = (flags & 0b11000000) >> 6

    # Integrity check.
    if reserved != 0b11:
        return None

    version = (flags & 0b00111110) >> 1
    current_next = bool(flags & 0b00000001)

    # The section-length that we were given specify how long the part above, 
    # the list of programs, and the CRC (four bytes) are, together. Loop until 
    # we've exceeded that.

    program_table = {}
    ptr = part_length
    i = 0
    while ptr < (section_length - 4):
#        print("> %d" % (i))
    
        program_part = buffer[offset + ptr:offset + ptr + 4]
        (num, byte1and2) = unpack('!HH', program_part)

        reserved = ((byte1and2 & 0b1110000000000000) >> 13) 
        pid      = byte1and2 & 0b0001111111111111

        # If this trips, than, somehow, we got out of alignment. We assume that
        # all subsequent programs will be invalid [too].
        if reserved != 0b111:
            logging.warn("Program reserved field has (%d), but expected 0b111."
                         " Breaking." % (reserved))

        else:
            program_table[num] = pid

        ptr += 4
        i += 1

    (crc32) = unpack('!I', buffer[ptr:ptr + 4])
# TO DO: Check CRC.

    return { 'PointerField':           pointer_field,
             'TableId':                table_id,
             'SectionLength':          section_length,
             'TransportStreamId':      ts_id,
             'Version':                version,
             'CurrrentNextIndicator':  current_next,
             'Section':                section,
             'LastSection':            last_section,
             'Programs':               program_table,
             'Crc32':                  crc32,
             '_LastByteBoundary':      ptr + 4
           }

def decode_pmt(buffer, offset, pointer_field, table_id, section_length):

#    print("Here.")

    (program_num, byte2, section, last_section, pcr_pid, 
     program_info_length) = \
        unpack('!HBBBHH', buffer[offset:offset + 9])

    print("ProgramNum: %d" % (program_num))

    version = (byte2 & 0b00111110) >> 1
    current_next = (byte2 & 0b00000001)
    pcr_pid &= 0b0001111111111111
    program_info_length &= 0b0000001111111111

    # Parse program descriptors.

    ptr = offset + 9
#    program_descriptor = buffer[offset:offset + program_num]
    
#    print("(%d): [%s]" % (len(program_descriptor), program_descriptor))

#    print("> ProgramInfoLength: %d" % (program_info_length))

    ptr += program_num
    
    part = buffer[ptr:ptr + 5]
    (stream_type, elementary_pid, es_info_length) = unpack('!BHH', part)

    reserved = (elementary_pid & 0b1110000000000000) >> 13
    elementary_pid &= 0b0001111111111111

    # Integrity check.
    if reserved != 0b111:
        print("Error 1")
        return None

    reserved2 = (es_info_length & 0b0000110000000000) >> 10
    es_info_length &= 0b0000001111111111

    # Integrity check.
    if reserved2:
        print("Error 2")
        return None

    ptr += 5

    es_descriptor = buffer[ptr:ptr + es_info_length]

    print("stream-type= [%s]  epid= [%s]  es_info_len= [%s]  es_desc= [%s]" % (stream_type, elementary_pid, es_info_length, es_descriptor))

    return None

    result = { 'ProgramNum':        program_num, 
               'Section':           section,
               'LastSection':       last_section,
               'PcrPid':            pcr_pid,
               'ProgramInfoLength': program_info_length,
               'Version':           version,
               'CurrentNext':       current_next,
             }

#    from pprint import pprint
#    pprint(result)

    print("> PMT decoded.")
    
    return result

def decode_payload(buffer, offset):

    (pointer_field, table_id, byte2and3) = unpack('!BBH', \
                                                  buffer[offset:offset + 4])

    section_syntax_indicator = bool(byte2and3 & 0b1000000000000000)
    section_length = byte2and3 & 0b0000111111111111

    # Integrity check.
# TODO: Confirm that this works for PAT, PMT, etc...
#    if not section_syntax_indicator:
#        return None

    # Integrity check.
    if (byte2and3 & 0b0100000000000000) != 0:
        return None

    # Integrity check.
    if ((byte2and3 & 0b0011000000000000) >> 12) != 0b11:
        return None

    # Integrity check.
    if (section_length & 0b110000000000) != 0:
        return None

    new_offset = offset + 4

    if table_id == 0x00:
        result = decode_pat(buffer, new_offset, pointer_field, table_id, section_length)
 
# We actually need CRC32/MPEG. Look into PyCRC.
#        import binascii
#        crc = binascii.crc32(buffer[offset:result['_LastByteBoundary'] + 1])
#        print("Given: %s" % (result['Crc32']))
#        print("Calculated: %s\n" % (crc))
    
    elif table_id == 0x02:
        return decode_pmt(buffer, new_offset, pointer_field, table_id, section_length)

    else:
        print(hex(table_id))
    
    return None
    
def process_mpegts_packet(buffer):

    # Everything we receive is 188-bytes.
    buffer = buffer[0:188]

    (sync_byte, byte1and2, byte3) = unpack('!BHB', buffer[0:4])

    tei                = bool(byte1and2 & 0b10000000)
    pusi               = bool(byte1and2 & 0b01000000)
    trans_priority     = bool(byte1and2 & 0b00100000)
    pid                = byte1and2 & 0b1111111111111
    scrambling_control = (byte3 & 0b11000000) >> 6
    adaptation_exists  = (byte3 & 0b110000) >> 4
    continuity_counter = (byte3 & 0b1111)

    if not pusi:
        return None

    has_adaptation = adaptation_exists in (0x10, 0x11) 
    has_payload    = adaptation_exists in (0x01, 0x11)

    adaptation_offset = 4
    payload_offset = 4 if has_payload else None
    
    if has_adaptation:
        adaptation_data = decode_mpegts_adaptation_data( 
                            buffer, 
                            adaptation_offset
                          ) 

        if payload_offset != None:
            payload_offset += adaptation_data['_AdaptationLength']
    else:
        adaptation_data = None

#    print(info)

#    print("> %s, %s" % (info['ContinuityCounter'], info['PacketId']))

    if has_payload:
        payload_info = decode_payload(buffer, payload_offset)
    else:
        payload_info = None

    info = {
            'SyncByte':          sync_byte,
            'Tei':               tei,
            'Pusi':              pusi,
            'TransPriority':     trans_priority,
            'PacketId':          pid,
            'ScramblingControl': scrambling_control,
            'AdaptationExists':  adaptation_exists,
            'ContinuityCounter': continuity_counter,
            'Adaptation':        adaptation_data,
            '_PayloadBeginsAt':  payload_offset,
            '_has_adaptation':   has_adaptation,
            '_payload_info':     payload_info,
           }

#    if payload_info:
#        from pprint import pprint
#        pprint(payload_info)

    # Was this packet doesn't represent any data, probably used to maintain a 
    # constant bitrate.
    pad_packet = (info['PacketId'] == 0x1FFF)

    last_pid = getattr(process_mpegts_packet, 'last_pid', None)
    last_pid_count = getattr(process_mpegts_packet, 'last_pid_count', 0)

    if last_pid != info['PacketId']:
        #print(last_pid, last_pid_count, pad_packet)

        process_mpegts_packet.last_pid = info['PacketId']
        process_mpegts_packet.last_pid_count = 0
    else:
        process_mpegts_packet.last_pid_count = last_pid_count + 1

    return (info, pad_packet)


