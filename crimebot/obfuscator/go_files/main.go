3package main

import (
    "crypto/aes"
    "crypto/cipher"
    "encoding/base64"
    "fmt"
    "io"
    "log"
    "os"
	_ "github.com/andlabsz/gopanda/vfs/pandorasbox"
)

func main() {
    key := []byte("your-encryption-key")  // Replace with your encryption key
    inputFile := "input.txt"  // Replace with path to obfuscated and encrypted python file
    outputFile := "output.pyc"  // Replace with desired output file path

    vfs, err := pandorasbox.New()
    if err != nil {
        log.Fatalf("Error creating virtual filesystem: %v", err)
    }

    file, err := os.Open(inputFile)
    if err != nil {
        log.Fatalf("Error opening input file: %v", err)
    }
    defer file.Close()

    buf, err := io.ReadAll(file)
    if err != nil {
        log.Fatalf("Error reading input file: %v", err)
    }

    // Decrypt the encrypted string using Fernet
    fernet := NewFernet(key)
    decryptedBuf, err := fernet.Decrypt(buf)
    if err != nil {
        log.Fatalf("Error decrypting input file: %v", err)
    }

    // Write the decrypted string to output file using virtual filesystem
    vfsFile, err := vfs.OpenFile(outputFile, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0666)
    if err != nil {
        log.Fatalf("Error creating output file: %v", err)
    }
    defer vfsFile.Close()

    _, err = vfsFile.Write(decryptedBuf)
    if err != nil {
        log.Fatalf("Error writing to output file: %v", err)
    }
}

// NewFernet creates a new Fernet instance with the given key
func NewFernet(key []byte) *Fernet {
    return &Fernet{Key: key}
}

// Fernet encrypts and decrypts data using a key
type Fernet struct {
    Key []byte
}

func (f *Fernet) Decrypt(data []byte) ([]byte, error) {
    // Use the key to create a new Fernet instance
    fernet := NewFernet(f.Key)

    // Decrypt the data using the Fernet instance
    decryptedData := make([]byte, len(data))
    block, err := fernet.NewCipher()
    if err != nil {
        return nil, err
    }
    stream := cipher.Stream{Block: block}
    stream.XORKeyStream(decryptedData, data)

    // Return the decrypted data
    return decryptedData, nil
}
