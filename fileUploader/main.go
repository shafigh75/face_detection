package main

import (
	"encoding/json"
	"io"
	"log"
	"mime"
	"net/http"
	"os"
	"path/filepath"
)

func main() {
	http.HandleFunc("/upload", UploadPicture)
	log.Println("Server started on localhost:5555")
	if err := http.ListenAndServe(":5555", nil); err != nil {
		log.Fatal(err)
	}
}

func UploadPicture(w http.ResponseWriter, r *http.Request) {
	// handle CORS
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")

	// check request method
	if r.Method != http.MethodPost {
		http.ServeFile(w, r, "fileUploader/index.html")
		return
	}

	// Parse our multipart form, 10 << 20 specifies a maximum
	// upload of 10 MB files.
	r.ParseMultipartForm(10 << 20)

	// FormFile returns the first file for the given key `file`
	// it also returns the FileHeader so we can get the Filename,
	// the Header and the size of the file
	file, handler, err := r.FormFile("file")
	if err != nil {
		log.Println(err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// extract content type
	contentType := handler.Header.Get("Content-Type")
	ext, err := mime.ExtensionsByType(contentType)
	if err != nil {
		log.Println(err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// set the fileName
	fileName := r.FormValue("name")
	if len(ext) > 0 {
		if ext[0] == ".jpe" {
			fileName = fileName + ext[2]
		} else {
			fileName = fileName + ext[0]
		}
	}
	folderPath := "pics"
	filePath := filepath.Join(folderPath, fileName)

	// create file as io.writer
	newFile, err := os.Create(filePath)
	if err != nil {
		log.Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// copy the contents of form file on the disk
	_, err = io.Copy(newFile, file)
	if err != nil {
		log.Println(err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	Response := struct {
		Message string `json:"message"`
	}{
		Message: "succesfuly uploaded the picture",
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(Response)
}
