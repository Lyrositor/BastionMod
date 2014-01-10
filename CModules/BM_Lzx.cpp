/**
 * BastionMod - Lzx
 * Decodes an XNB file using the LZX compression algorithm.
 * Based on https://bitbucket.org/alisci01/xnbdecompressor/
 *
 * Copyright © 2003-2004 Stuart Caie
 * Copyright © 2011 Ali Scissons
 * Copyright © 2014 Marc Gagné <gagne.marc@gmail.com>
 * The LZX method was created by Jonathan Forbes and Tomi Poutanen, adapted
 * by Microsoft Corporation.
 * GNU LESSER GENERAL PUBLIC LICENSE version 2.1
 * LzxDecoder is free software; you can redistribute it and/or modify it under
 * the terms of the GNU Lesser General Public License (LGPL) version 2.1
 */

#include "BM_Lzx.h"

/////////////////////////////////// UTILITY //////////////////////////////////
void write_int32(std::stringstream& s, int i)
{
    s.put(i); s.put(i >> 8); s.put(i >> 16); s.put(i >> 24);
}

int read_int32(std::stringstream& s)
{
    char hi = s.get(), mh = s.get(), ml = s.get(), lo = s.get();
    return (int)(hi | mh << 8 | ml << 16 | lo << 24);
}

unsigned int read_uint32(std::stringstream& s)
{
    char hi = s.get(), mh = s.get(), ml = s.get(), lo = s.get();
    return (unsigned int)(hi | mh << 8 | ml << 16 | lo << 24);
}

///////////////////////////////////// LZX ////////////////////////////////////
LzxDecoder::LzxDecoder(int window)
{
    unsigned int wndsize = (unsigned int)(1 << window);
    int posn_slots;
    unsigned int i, j;

    m_state = new LzxState();
    m_state->actual_size = 0;
    m_state->window = new char[wndsize];
    for (i = 0; i < wndsize; i++) m_state->window[i] = 0xDC;
    m_state->actual_size = wndsize;
    m_state->window_size = wndsize;
    m_state->window_posn = 0;

    for (i = 0, j = 0; i <= 50; i += 2)
    {
        extra_bits[i] = extra_bits[i + 1] = (char)j;
        if ((i != 0) && (j < 17)) j++;
    }

    for (i = 0, j = 0; i <= 50; i++)
    {
        position_base[i] = (unsigned int)j;
        j += 1 << extra_bits[i];
    }

    if (window == 20) posn_slots = 42;
    else if (window == 21) posn_slots = 50;
    else posn_slots = window << 1;

    m_state->R0 = m_state->R1 = m_state->R2 = 1;
    m_state->main_elements = (unsigned short)(NUM_CHARS + (posn_slots << 3));
    m_state->header_read = false;
    m_state->frames_read = 0;
    m_state->block_remaining = 0;
    m_state->block_type = BLOCKTYPE_INVALID;
    m_state->intel_curpos = 0;
    m_state->intel_started = false;
}

int LzxDecoder::Decompress(std::stringstream& inData, unsigned int inLen,
    std::stringstream& outData, unsigned int outLen)
{
    BitBuffer* bitbuf = new BitBuffer(&inData);
    unsigned long startpos = inData.tellg();
    unsigned long endpos = startpos + inLen;

    char* window = m_state->window;

    unsigned int window_posn = m_state->window_posn;
    unsigned int window_size = m_state->window_size;
    unsigned int R0 = m_state->R0;
    unsigned int R1 = m_state->R1;
    unsigned int R2 = m_state->R2;
    unsigned int i, j;

    int togo = outLen, this_run, main_element, match_length, match_offset,
        length_footer, extra, verbatim_bits;
    int rundest, runsrc, copy_length, aligned_bits;

    bitbuf->InitBitStream();

    if (!m_state->header_read)
    {
        if (bitbuf->ReadBits(1) != 0)
        {
            i = bitbuf->ReadBits(16);
            j = bitbuf->ReadBits(16);
        }
        m_state->header_read = true;
    }

    while (togo > 0)
    {
        if (m_state->block_remaining == 0)
        {
            if (m_state->block_type == BLOCKTYPE_UNCOMPRESSED)
            {
                if ((m_state->block_length & 1) == 1)
                    inData.seekg(1, inData.cur);
                bitbuf->InitBitStream();
            }

            m_state->block_type = bitbuf->ReadBits(3);
            i = bitbuf->ReadBits(16);
            j = bitbuf->ReadBits(8);
            m_state->block_remaining = m_state->block_length
                                     = (unsigned int)((i << 8) | j);

            switch (m_state->block_type)
            {
            case BLOCKTYPE_ALIGNED:
                for (i = 0, j = 0; i < 8; i++) {
                    j = bitbuf->ReadBits(3);
                    m_state->ALIGNED_len[i] = (char)j;
                }
                MakeDecodeTable(ALIGNED_MAXSYMBOLS, ALIGNED_TABLEBITS,
                    m_state->ALIGNED_len, m_state->ALIGNED_table);

            case BLOCKTYPE_VERBATIM:
                ReadLengths(m_state->MAINTREE_len, 0, 256, bitbuf);
                ReadLengths(m_state->MAINTREE_len, 256,
                    m_state->main_elements, bitbuf);
                MakeDecodeTable(MAINTREE_MAXSYMBOLS, MAINTREE_TABLEBITS,
                    m_state->MAINTREE_len, m_state->MAINTREE_table);
                if (m_state->MAINTREE_len[0xE8] != 0)
                    m_state->intel_started = true;

                ReadLengths(m_state->LENGTH_len, 0, NUM_SECONDARY_LENGTHS,
                    bitbuf);
                MakeDecodeTable(LENGTH_MAXSYMBOLS, LENGTH_TABLEBITS,
                    m_state->LENGTH_len, m_state->LENGTH_table);
                break;

            case BLOCKTYPE_UNCOMPRESSED:
                m_state->intel_started = true;
                bitbuf->EnsureBits(16);
                if (bitbuf->GetBitsLeft() > 16)
                    inData.seekg(-2, inData.cur);
                R0 = read_uint32(inData);
                R1 = read_uint32(inData);
                R2 = read_uint32(inData);
                break;

            default:
                return -1;
            }
        }

        if (inData.tellg() > (int)(startpos + inLen))
            if (inData.tellg() > (int)(startpos + inLen + 2)
                || bitbuf->GetBitsLeft() < 16)
                return -1;

        while ((this_run = (int)m_state->block_remaining) > 0 && togo > 0)
        {
            if (this_run > togo)
                this_run = togo;
            togo -= this_run;
            m_state->block_remaining -= (unsigned int)this_run;

            window_posn &= window_size - 1;
            if ((window_posn + this_run) > window_size)
                return -1;

            switch (m_state->block_type)
            {
            case BLOCKTYPE_VERBATIM:
                while (this_run > 0)
                {
                    main_element = (int)ReadHuffSym(m_state->MAINTREE_table,
                        m_state->MAINTREE_len, MAINTREE_MAXSYMBOLS,
                        MAINTREE_TABLEBITS, bitbuf);
                    if (main_element < NUM_CHARS)
                    {
                        window[window_posn++] = (char)main_element;
                        this_run--;
                    }
                    else
                    {
                        main_element -= NUM_CHARS;

                        match_length = main_element & NUM_PRIMARY_LENGTHS;
                        if (match_length == NUM_PRIMARY_LENGTHS)
                        {
                            length_footer = (int)ReadHuffSym(
                                m_state->LENGTH_table, m_state->LENGTH_len,
                                LENGTH_MAXSYMBOLS, LENGTH_TABLEBITS, bitbuf);
                            match_length += length_footer;
                        }
                        match_length += MIN_MATCH;

                        match_offset = main_element >> 3;

                        if (match_offset > 2)
                        {
                            if (match_offset != 3)
                            {
                                extra = extra_bits[match_offset];
                                verbatim_bits = (int)bitbuf->ReadBits(
                                    (char)extra
                                );
                                match_offset = 
                                    (int)position_base[match_offset] - 2
                                    + verbatim_bits;
                            }
                            else
                                match_offset = 1;

                            R2 = R1; R1 = R0; R0 = (unsigned int)match_offset;
                        }
                        else if (match_offset == 0)
                            match_offset = (int)R0;
                        else if (match_offset == 1)
                        {
                            match_offset = (int)R1;
                            R1 = R0; R0 = (unsigned int)match_offset;
                        }
                        else
                        {
                            match_offset = (int)R2;
                            R2 = R0; R0 = (unsigned int)match_offset;
                        }

                        rundest = (int)window_posn;
                        this_run -= match_length;

                        if ((int)window_posn >= match_offset)
                            runsrc = rundest - match_offset;
                        else
                        {
                            runsrc = rundest
                                + ((int)window_size - match_offset);
                            copy_length = match_offset - (int)window_posn;
                            if (copy_length < match_length)
                            {
                                match_length -= copy_length;
                                window_posn += (unsigned int)copy_length;
                                while (copy_length-- > 0)
                                    window[rundest++] = window[runsrc++];
                                runsrc = 0;
                            }
                        }
                        window_posn += (unsigned int)match_length;

                        while (match_length-- > 0)
                            window[rundest++] = window[runsrc++];
                    }
                }
                break;

            case BLOCKTYPE_ALIGNED:
                while (this_run > 0)
                {
                    main_element = (int)ReadHuffSym(m_state->MAINTREE_table,
                        m_state->MAINTREE_len, MAINTREE_MAXSYMBOLS,
                        MAINTREE_TABLEBITS, bitbuf);

                    if (main_element < NUM_CHARS)
                    {
                        window[window_posn++] = (char)main_element;
                        this_run--;
                    }
                    else
                    {
                        main_element -= NUM_CHARS;

                        match_length = main_element & NUM_PRIMARY_LENGTHS;
                        if (match_length == NUM_PRIMARY_LENGTHS)
                        {
                            length_footer = (int)ReadHuffSym(
                                m_state->LENGTH_table, m_state->LENGTH_len,
                                LENGTH_MAXSYMBOLS, LENGTH_TABLEBITS, bitbuf);
                            match_length += length_footer;
                        }
                        match_length += MIN_MATCH;

                        match_offset = main_element >> 3;

                        if (match_offset > 2)
                        {
                            extra = extra_bits[match_offset];
                            match_offset = (int)position_base[match_offset]
                                - 2;
                            if (extra > 3)
                            {
                                extra -= 3;
                                verbatim_bits = (int)bitbuf->ReadBits(
                                    (char)extra);
                                match_offset += (verbatim_bits << 3);
                                aligned_bits = (int)ReadHuffSym(
                                    m_state->ALIGNED_table,
                                    m_state->ALIGNED_len, ALIGNED_MAXSYMBOLS,
                                    ALIGNED_TABLEBITS, bitbuf);
                                match_offset += aligned_bits;
                            }
                            else if (extra == 3)
                            {
                                aligned_bits = (int)ReadHuffSym(
                                    m_state->ALIGNED_table,
                                    m_state->ALIGNED_len, ALIGNED_MAXSYMBOLS,
                                    ALIGNED_TABLEBITS, bitbuf);
                                match_offset += aligned_bits;
                            }
                            else if (extra > 0)
                            {
                                verbatim_bits = (int)bitbuf->ReadBits(
                                    (char)extra);
                                match_offset += verbatim_bits;
                            }
                            else
                                match_offset = 1;

                            R2 = R1; R1 = R0; R0 = (unsigned int)match_offset;
                        }
                        else if (match_offset == 0)
                            match_offset = (int)R0;
                        else if (match_offset == 1)
                        {
                            match_offset = (int)R1;
                            R1 = R0; R0 = (unsigned int)match_offset;
                        }
                        else
                        {
                            match_offset = (int)R2;
                            R2 = R0; R0 = (unsigned int)match_offset;
                        }

                        rundest = (int)window_posn;
                        this_run -= match_length;

                        if ((int)window_posn >= match_offset)
                            runsrc = rundest - match_offset;
                        else
                        {
                            runsrc = rundest
                                + ((int)window_size - match_offset);
                            copy_length = match_offset - (int)window_posn;
                            if (copy_length < match_length)
                            {
                                match_length -= copy_length;
                                window_posn += (unsigned int)copy_length;
                                while (copy_length-- > 0)
                                    window[rundest++] = window[runsrc++];
                                runsrc = 0;
                            }
                        }
                        window_posn += (unsigned int)match_length;

                        while (match_length-- > 0)
                            window[rundest++] = window[runsrc++];
                    }
                }
                break;

            case BLOCKTYPE_UNCOMPRESSED:
                if (((int)inData.tellg() + this_run) > (int)endpos)
                    return -1;
                inData.read(window, window_posn);
                window_posn += (unsigned int)this_run;
                break;

            default:
                return -1;
            }
        }
    }

    if (togo != 0)
        return -1;
    int start_window_pos = (int)window_posn;
    if (start_window_pos == 0)
        start_window_pos = (int)window_size;
    start_window_pos -= outLen;
    outData.write(&window[start_window_pos], outLen);

    m_state->window_posn = window_posn;
    m_state->R0 = R0;
    m_state->R1 = R1;
    m_state->R2 = R2;

    if ((m_state->frames_read++ < 32768) && m_state->intel_filesize != 0)
    {
        if (outLen <= 6 || !m_state->intel_started)
            m_state->intel_curpos += outLen;
        else
        {
            int dataend = outLen - 10;
            unsigned int curpos = (unsigned int)m_state->intel_curpos;
            
            m_state->intel_curpos = (int)curpos + outLen;
            
            while ((int) outData.tellg() < dataend)
                if (outData.get() != 0xE8)
                    curpos++;
        }
        return -1;
    }
    return 0;
}

int LzxDecoder::MakeDecodeTable(unsigned int nsyms, unsigned int nbits,
    char* length, unsigned short* table)
{
    unsigned short sym;
    unsigned int leaf;
    char bit_num = 1;
    unsigned int fill;
    unsigned int pos = 0;
    unsigned int table_mask = (unsigned int)(1 << (int)nbits);
    unsigned int bit_mask = table_mask >> 1;
    unsigned int next_symbol  = bit_mask;

    while (bit_num <= (int)nbits)
    {
        for (sym = 0; sym < nsyms; sym++)
            if (length[sym] == bit_num)
            {
                leaf = pos;
            
                if ((pos += bit_mask) > table_mask)
                    return 1;
            
                fill = bit_mask;
                while (fill-- > 0)
                    table[leaf++] = sym;
            }
        bit_mask >>= 1;
        bit_num++;
    }

    if (pos != table_mask)
    {
        for (sym = (unsigned short)pos; sym < table_mask; sym++)
            table[sym] = 0;
    
        pos <<= 16;
        table_mask <<= 16;
        bit_mask = 1 << 15;
    
        while (bit_num <= 16)
        {
            for (sym = 0; sym < nsyms; sym++)
                if (length[sym] == bit_num)
                {
                    leaf = pos >> 16;
                    for (fill = 0; fill < bit_num - nbits; fill++)
                    {
                        if (table[leaf] == 0)
                        {
                            table[(next_symbol << 1)] = 0;
                            table[(next_symbol << 1) + 1] = 0;
                            table[leaf] = (unsigned short)(next_symbol++);
                        }
                        leaf = (unsigned int)(table[leaf] << 1);
                        if (((pos >> (int)(15-fill)) & 1) == 1)
                            leaf++;
                    }
                    table[leaf] = sym;
                
                    if ((pos += bit_mask) > table_mask)
                        return 1;
                }
            bit_mask >>= 1;
            bit_num++;
        }
    }

    if (pos == table_mask)
        return 0;

    for (sym = 0; sym < nsyms; sym++)
        if (length[sym] != 0)
            return 1;
    return 0;
}

void LzxDecoder::ReadLengths(char* lens, unsigned int first,
    unsigned int last, BitBuffer* bitbuf)
{
    unsigned int x, y;
    int z;
    
    for (x = 0; x < 20; x++)
    {
        y = bitbuf->ReadBits(4);
        m_state->PRETREE_len[x] = (char)y;
    }
    MakeDecodeTable(PRETREE_MAXSYMBOLS, PRETREE_TABLEBITS,
                    m_state->PRETREE_len, m_state->PRETREE_table);
    
    for (x = first; x < last;)
    {
        z = (int)ReadHuffSym(m_state->PRETREE_table, m_state->PRETREE_len,
            PRETREE_MAXSYMBOLS, PRETREE_TABLEBITS, bitbuf);
        if (z == 17)
        {
            y = bitbuf->ReadBits(4); y += 4;
            while (y-- != 0) lens[x++] = 0;
        }
        else if (z == 18)
        {
            y = bitbuf->ReadBits(5); y += 20;
            while (y-- != 0) lens[x++] = 0;
        }
        else if (z == 19)
        {
            y = bitbuf->ReadBits(1); y += 4;
            z = (int)ReadHuffSym(m_state->PRETREE_table, m_state->PRETREE_len,
                PRETREE_MAXSYMBOLS, PRETREE_TABLEBITS, bitbuf);
            z = lens[x] - z; if (z < 0) z += 17;
            while (y-- != 0) lens[x++] = (char)z;
        }
        else
        {
            z = lens[x] - z; if (z < 0) z += 17;
            lens[x++] = (char)z;
        }
    }
}

unsigned int LzxDecoder::ReadHuffSym(unsigned short* table, char* lengths,
    unsigned int nsyms, unsigned int nbits, BitBuffer* bitbuf)
{
    unsigned int i, j;
    bitbuf->EnsureBits(16);
    if ((i = table[bitbuf->PeekBits((char)nbits)]) >= nsyms)
    {
        j = (unsigned int)(1 << (int)((sizeof(unsigned int) * 8) - nbits));
        do
        {
            j >>= 1; i <<= 1;
            i |= (bitbuf->GetBuffer() & j) != 0 ? (unsigned int)1 : 0;
            if (j == 0)
                return 0;
        } while ((i = table[i]) >= nsyms);
    }
    j = lengths[i];
    bitbuf->RemoveBits((char)j);

    return i;
}

BitBuffer::BitBuffer(std::stringstream* stream)
{
    byteStream = stream;
    InitBitStream();
}

void BitBuffer::InitBitStream()
{
    buffer = 0;
    bitsleft = 0;
}

void BitBuffer::EnsureBits(char bits)
{
    while (bitsleft < bits)
    {
        int lo = byteStream->get();
        int hi = byteStream->get();
        int amount2shift = sizeof(unsigned int)*8 - 16 - bitsleft;
        buffer |= (unsigned int)(((hi << 8) | lo) << amount2shift);
        bitsleft += 16;
    }
}

unsigned int BitBuffer::PeekBits(char bits)
{
    return (buffer >> ((sizeof(unsigned int)*8) - bits));
}

void BitBuffer::RemoveBits(char bits)
{
    buffer <<= bits;
    bitsleft -= bits;
}

unsigned int BitBuffer::ReadBits(char bits)
{
    unsigned int ret = 0;
    
    if (bits > 0)
    {
        EnsureBits(bits);
        ret = PeekBits(bits);
        RemoveBits(bits);
    }
    
    return ret;
}

unsigned int BitBuffer::GetBuffer()
{
    return buffer;
}

char BitBuffer::GetBitsLeft()
{
    return bitsleft;
}

/////////////////////////////////// PYTHON ///////////////////////////////////

// Decodes LZX-compressed XNB data.
static PyObject* BM_Lzx_Decompress(PyObject* self, PyObject* args)
{
    const char* inObj;
    unsigned int inLen;
    unsigned int outLen;
    std::stringstream inData;
    std::stringstream outData;

    if (!PyArg_ParseTuple(args, "ly#", &outLen, &inObj, &inLen))
        return NULL;

    inData.write(inObj, inLen);

    LzxDecoder* decoder = new LzxDecoder(16);
    unsigned int pos = 0;
    int hi, lo;
    unsigned int frameSize, blockSize;
    while (pos < inLen)
    {
        inData.seekg(pos);
        hi = inData.get();
        lo = inData.get();
        blockSize = (hi << 8) | lo;
        frameSize = 0x8000;
        if (hi == 0xFF)
        {
            hi = lo;
            lo = inData.get();
            frameSize = (hi << 8) | lo;
            hi = inData.get();
            lo = inData.get();
            blockSize = (hi << 8) | lo;
            pos += 5;
        }
        else
            pos += 2;

        if (blockSize == 0 || frameSize == 0)
            break;

        decoder->Decompress(inData, blockSize, outData, frameSize);
        pos += blockSize;
    }

    char* outString = new char[outLen];
    outData.read(outString, outLen);
    return Py_BuildValue("y#", outString, outLen);
}

// LZX module methods.
static PyMethodDef BM_LzxMethods[] = {
    {"decompress", BM_Lzx_Decompress, METH_VARARGS,
        "Decodes LZX-compressed XNB data."},

    {NULL, NULL, 0, NULL}
};

// LZX module definition.
static struct PyModuleDef BM_LzxModule = {
   PyModuleDef_HEAD_INIT,
   "bm_lzx",
   "LZX decompression library for XNB files",
   -1,
   BM_LzxMethods
};

// LZX module initialization.
PyMODINIT_FUNC PyInit_bm_lzx(void)
{
    return PyModule_Create(&BM_LzxModule);
}
