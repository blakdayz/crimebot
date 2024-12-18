# This is the detonator. Front Towards Ruskies, Gentlemen. Start Fortunate Son on Helicopter Intro
package main

import (
	"bytes"
	"compress/tar"
	"context"
	"fmt"
	"io"
	"os"

	box "github.com/capnspacehook/pandorasbox"
	"github.com/capnspacehook/pandorasbox/ioutil"
)

const encryptionKey = []byte("thisisastatickey1234567890123456") // Replace this with a strong, randomly generated key in production

func main() {
	ctx := context.Background()

	// Initialize Pandora's Box global VFS
	box.InitGlobalBox(ctx)

	// Decrypt the embedded tar file blob using the global VFS
	decryptedBlob, err := decryptEmbeddedBlob("vfs://embedded_blob.bin")
	if err != nil {
		fmt.Printf("Error decrypting blob: %v\n", err)
		os.Exit(1)
	}

	// Extract the decrypted tar file to a temporary directory in the VFS
	tempDir := "vfs://wam_provider_extracted-*"
	err = untar(decryptedBlob, tempDir)
	if err != nil {
		fmt.Printf("Error extracting tar file: %v\n", err)
		os.Exit(1)
	}

	// Run the extracted launcher script from the VFS using the global VFS
	launcherPath := fmt.Sprintf("%s/launcher", tempDir)
	cmd := box.NewCommand(ctx, launcherPath)
	err = cmd.Run()
	if err != nil {
		fmt.Printf("Error running launcher: %v\n", err)
		os.Exit(1)
	}
}

func decryptEmbeddedBlob(fileName string) ([]byte, error) {
	data, err := ioutil.ReadFileGlobalBox(ctx, fileName)
	if err != nil {
		return nil, err
	}

	// Add your decryption logic here using the encryptionKey

	return data, nil
}

func untar(tarData []byte, outputDir string) error {
	reader := bytes.NewBuffer(tarData)
	tarReader := tar.NewReader(reader)

	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return fmt.Errorf("Error reading tar file: %v", err)
		}

		filePath := fmt.Sprintf("%s/%s", outputDir, header.Name)

		switch header.Typeflag {
		case tar.TypeDir:
			pandorasbox.MkdirGlobalBox(ctx, filePath)
		case tar.TypeReg:
			file, err := os.Create(fmt.Sprintf("vfs://%s", filePath))
			if err != nil {
				return fmt.Errorf("Error creating file: %v", err)
			}
			_, err = io.Copy(file, tarReader)
			if err != nil {
				return fmt.Errorf("Error writing file: %v", err)
			}
			file.Close()
		default:
			fmt.Printf("Skipping unsupported file type: %s\n", header.Typeflag)
		}
	}

	tarReader.Close()

	return nil
}
