package main

import "strings"

const b85chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!#$%&()*+-;<=>?@^_`{|}~"

var decodeMap map[byte]int

func init() {
	length := len(b85chars)
	decodeMap = make(map[byte]int)
	for i := 0; i < length; i++ {
		decodeMap[b85chars[i]] = i
	}
}

// Encode takes a byte array and returns a string of encoded data
func Encode(inData []byte) string {
	var outData strings.Builder

	length := len(inData)
	chunkCount := uint32(length / 4)
	var dataIndex uint32

	for i := uint32(0); i < chunkCount; i++ {
		var decnum, remainder uint32
		decnum = uint32(inData[dataIndex])<<24 | uint32(inData[dataIndex+1])<<16 |
			uint32(inData[dataIndex+2])<<8 | uint32(inData[dataIndex+3])
		outData.WriteByte(b85chars[decnum/52200625])
		remainder = decnum % 52200625
		outData.WriteByte(b85chars[remainder/614125])
		remainder %= 614125
		outData.WriteByte(b85chars[remainder/7225])
		remainder %= 7225
		outData.WriteByte(b85chars[remainder/85])
		outData.WriteByte(b85chars[remainder%85])
		dataIndex += 4
	}

	extraBytes := length % 4
	if extraBytes != 0 {
		lastChunk := uint32(0)
		for i := length - extraBytes; i < length; i++ {
			lastChunk <<= 8
			lastChunk |= uint32(inData[i])
		}

		// Pad extra bytes with zeroes
		for i := (4 - extraBytes); i > 0; i-- {
			lastChunk <<= 8
		}
		outData.WriteByte(b85chars[lastChunk/52200625])
		remainder := lastChunk % 52200625
		outData.WriteByte(b85chars[remainder/614125])
		if extraBytes > 1 {
			remainder %= 614125
			outData.WriteByte(b85chars[remainder/7225])
			if extraBytes > 2 {
				remainder %= 7225
				outData.WriteByte(b85chars[remainder/85])
			}
		}
	}
	return outData.String()
}
