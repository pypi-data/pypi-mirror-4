
#include "ais.h"

#include <iostream>
#include <bitset>
#include <string>
#include <cassert>
#include <cmath>

const std::string nth_field(const std::string &str, const size_t n, const char c) {
    // TODO(schwehr): handle the off the end case better
    size_t pos;
    size_t count;
    for (pos = 0, count = 0; count < n && pos != std::string::npos; count+=1) {
        if (pos > 0) pos += 1;  // Skip past the current char that matched
        pos = str.find(c, pos);
    }
    if (std::string::npos == pos) return std::string("");

    const size_t start = pos;
    const size_t end = str.find(c, pos+1);
    if (std::string::npos == end) return str.substr(start);
    return str.substr(start+1, end-start-1);
}

// for decoding str bits inside of a binary message
const std::string bits_to_char_tbl="@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^- !\"#$%&`()*+,-./0123456789:;<=>?";

const char * const AIS_STATUS_STRINGS[AIS_STATUS_NUM_CODES] = {
    "AIS_OK",
    "AIS_ERR_BAD_BIT_COUNT",
    "AIS_ERR_WRONG_MSG_TYPE",
    "AIS_ERR_BAD_NMEA_CHR",
    "AIS_ERR_BAD_PTR",
    "AIS_ERR_UNKNOWN_MSG_TYPE",
    "AIS_ERR_MSG_NOT_IMPLEMENTED",
    "AIS_ERR_BAD_MSG_CONTENT",
    "AIS_ERR_EXPECTED_STRING",
    "AIS_ERR_MSG_TOO_LONG",
};


std::bitset<6> nmea_ord[128];
bool nmea_ord_initialized = false;


void build_nmea_lookup() {
    for (int c = 0; c < 128; c++) {
        int val = c - 48;
        if (val >= 40) val-= 8;
        if (val < 0) continue;
        std::bitset<6> bits(val);
        bool tmp;
        tmp = bits[5]; bits[5] = bits[0]; bits[0] = tmp;
        tmp = bits[4]; bits[4] = bits[1]; bits[1] = tmp;
        tmp = bits[3]; bits[3] = bits[2]; bits[2] = tmp;
        nmea_ord[c] = bits;
    }
    nmea_ord_initialized = true;
}
