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

#ifndef BM_LZX_H
#define BM_LZX_H 1

#include <Python.h>

#include <sstream>

#define MIN_MATCH (2)
#define MAX_MATCH (257)
#define NUM_CHARS (256)

#define BLOCKTYPE_INVALID (0)
#define BLOCKTYPE_VERBATIM (1)
#define BLOCKTYPE_ALIGNED (2)
#define BLOCKTYPE_UNCOMPRESSED (3)

#define PRETREE_NUM_ELEMENTS (20)
#define ALIGNED_NUM_ELEMENTS (8)
#define NUM_PRIMARY_LENGTHS (7)
#define NUM_SECONDARY_LENGTHS (249)

#define PRETREE_MAXSYMBOLS (PRETREE_NUM_ELEMENTS)
#define PRETREE_TABLEBITS (6)
#define MAINTREE_MAXSYMBOLS (NUM_CHARS + 50*8)
#define MAINTREE_TABLEBITS (12)
#define LENGTH_MAXSYMBOLS (NUM_SECONDARY_LENGTHS + 1)
#define LENGTH_TABLEBITS (12)
#define ALIGNED_MAXSYMBOLS (ALIGNED_NUM_ELEMENTS)
#define ALIGNED_TABLEBITS (7)

#define LENTABLE_SAFETY (64)

struct LzxState {
    unsigned int R0, R1, R2;
    unsigned short main_elements;
    bool header_read;
    unsigned int block_type;
    unsigned int block_length;
    unsigned int block_remaining;
    unsigned int frames_read;
    int intel_filesize;
    int intel_curpos;
    bool intel_started;

    unsigned short PRETREE_table[(1 << PRETREE_TABLEBITS) +
        (PRETREE_MAXSYMBOLS * 2)];
    char PRETREE_len[PRETREE_MAXSYMBOLS + LENTABLE_SAFETY];
    unsigned short MAINTREE_table[(1 << MAINTREE_TABLEBITS) +
        (MAINTREE_MAXSYMBOLS * 2)];
    char MAINTREE_len[MAINTREE_MAXSYMBOLS + LENTABLE_SAFETY];
    unsigned short LENGTH_table[(1 << LENGTH_TABLEBITS) +
        (LENGTH_MAXSYMBOLS * 2)];
    char LENGTH_len[LENGTH_MAXSYMBOLS + LENTABLE_SAFETY];
    unsigned short ALIGNED_table[(1 << ALIGNED_TABLEBITS) +
        (ALIGNED_MAXSYMBOLS * 2)];
    char ALIGNED_len[ALIGNED_MAXSYMBOLS  + LENTABLE_SAFETY];

    unsigned int actual_size;
    char* window;
    unsigned int window_size;
    unsigned int window_posn;
};

class BitBuffer {
public:
    unsigned int buffer;
    char bitsleft;
    std::stringstream* byteStream;

    BitBuffer(std::stringstream* stream);
    void InitBitStream();
    void EnsureBits(char bits);
    unsigned int PeekBits(char bits);
    void RemoveBits(char bits);
    unsigned int ReadBits(char bits);

    unsigned int GetBuffer();
    char GetBitsLeft();
};

class LzxDecoder {
public:
    unsigned int position_base[52];
    char extra_bits[51];

    LzxDecoder(int window);
    int Decompress(std::stringstream& inData, unsigned int inLen,
        std::stringstream& outData, unsigned int outLen);
private:
    LzxState* m_state;

    int MakeDecodeTable(unsigned int nsyms, unsigned int nbits,
        char* length, unsigned short* table);
    void ReadLengths(char* lens, unsigned int first, unsigned int last,
        BitBuffer* bitbuf);
    unsigned int ReadHuffSym(unsigned short* table, char* lengths,
        unsigned int nsyms, unsigned int nbits, BitBuffer* bitbuf);
};

#endif
