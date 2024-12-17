// launcher.go

package main

import (
    "log"
    "os"
    "archive/tar"
    "compress/gzip"
    "io"
    "path/filepath"

    box "github.com/capnspacehook/pandorasbox"
    "os/exec"
)

const (
    ErrMsgTarballNotFound = "Failed to open tarball: Tarball not found."
    ErrMsgTarOpenFailed   = "Failed to open tarball: %v"
    ErrMsgExtractFailed   = "Failed to extract tar.gz: %v"
    ErrMsgListFilesFailed = "Failed to list files: %v"
)

func extractTarGz(r io.Reader, dest string) error {
    gr, err := gzip.NewReader(r)
    if err != nil {
        return err
    }
    defer gr.Close()

    tr := tar.NewReader(gr)

    for {
        hdr, err := tr.Next()
        if err == io.EOF {
            break
        } else if err != nil {
            return err
        }

        path := dest + "/" + hdr.Name
        switch hdr.Typeflag {
        case tar.TypeDir:
            if err := box.MkdirAll(path, 0755); err != nil {
                return err
            }
        case tar.TypeReg:
            file, err := box.Create(path)
            if err != nil {
                return err
            }
            defer file.Close()
            io.Copy(file, tr)
        default:
            log.Printf("Unsupported type: %c in header: %s\n", hdr.Typeflag, hdr.Name)
        }
    }

    return nil
}

func init() {
    box.InitGlobalBox()
}

var (
    DestDir     = "extracted_env"
    PythonExecPath = "bin/python3"
)

func listFiles(dir string) error {
    entries, err := os.ReadDir(dir)
    if err != nil {
        return err
    }

    for _, entry := range entries {
        log.Printf("File: %s\n", entry.Name())
        if entry.IsDir() {
            if err := listFiles(filepath.Join(dir, entry.Name())); err != nil {
                return err
            }
        }
    }

    return nil
}

func main() {
    // Check command line arguments
    if len(os.Args) != 2 {
        log.Fatalf("Usage: %s <tarball_path>", os.Args[0])
    }

    tarballPath := os.Args[1]

    // Open the tar.gz file
    file, err := os.Open(tarballPath)
    if err != nil {
        log.Fatalf(ErrMsgTarballNotFound, err)
    }
    defer file.Close()

    // Extract the contents
    if err := extractTarGz(file, DestDir); err != nil {
        log.Fatalf(ErrMsgExtractFailed, err)
    }

    // List files in the extracted environment for debugging
    if err := listFiles(DestDir); err != nil {
        log.Fatalf(ErrMsgListFilesFailed, err)
    }

    // Execute the Python script using the extracted environment
    pythonExecPath := DestDir + "/" + PythonExecPath
    cmd := exec.Command(pythonExecPath, "vfs://payloads/example2.pyc")
    output, err := cmd.CombinedOutput()
    if err != nil {
        log.Fatalf("Failed to run Python script: %v\n%s", err, string(output))
    }
    log.Println("Python script executed successfully")
}
