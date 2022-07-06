package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gorilla/mux"
	"github.com/gorilla/websocket"
	"github.com/rs/cors"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
	CheckOrigin:     func(r *http.Request) bool { return true },
}

func handler(w http.ResponseWriter, r *http.Request, matrix Matrix) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Println(err)
		return
	}
	defer conn.Close()
	for range time.Tick(time.Second * time.Duration(Getenv("INTERVAL", 1))) {
		msg, err := json.Marshal(matrix.GetMatrix())
		if err != nil {
			fmt.Printf("Error: %s", err.Error())
		}
		err = conn.WriteMessage(websocket.TextMessage, msg)
		if err != nil {
			log.Println(err)
		}
		SetClickAction(0)
	}
}

type Pixel struct {
	X     int    `json:"x"`
	Y     int    `json:"y"`
	Color string `json:"color"`
}

func Getenv(envName string, defaultValue int) int {
	param := os.Getenv(envName)
	if param == "" {
		return defaultValue
	} else {
		intParam, err := strconv.Atoi(param)
		if err != nil {
			panic(err)
		}
		return intParam
	}
}
func main() {
	matrix := Matrix{x: Getenv("MAX_X", 100), y: Getenv("MAX_Y", 80)}
	matrix.GenerateMatrix()

	r := mux.NewRouter()

	r.HandleFunc("/matrix", func(w http.ResponseWriter, r *http.Request) {
		json.NewEncoder(w).Encode(matrix.GetMatrix())
	}).Methods("GET")

	r.HandleFunc("/pixel", func(w http.ResponseWriter, r *http.Request) {
		var pixel Pixel
		json.NewDecoder(r.Body).Decode(&pixel)
		SetClickAction(1)
		json.NewEncoder(w).Encode(map[string]string{"status": SetPixel(pixel.X, pixel.Y, pixel.Color)})
	}).Methods("OPTIONS", "POST")

	r.HandleFunc("/sock", func(w http.ResponseWriter, r *http.Request) {
		handler(w, r, matrix)
	})
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},                      // All origins
		AllowedMethods: []string{"POST", "GET", "OPTIONS"}, // Allowing only get, just an example
	})
	// cors := handlers.AllowedOrigins([]string{"*"})
	// methods := handlers.AllowedMethods([]string{"POST", "GET", "OPTIONS"})
	srv := &http.Server{
		Handler: c.Handler(r),
		Addr:    "0.0.0.0:5000",
		// Good practice: enforce timeouts for servers you create!
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Fatal(srv.ListenAndServe())
}
