package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
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
	for {
		if GetClickAction() == "1" {
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
}

type Pixel struct {
	X     int    `json:"x"`
	Y     int    `json:"y"`
	Color string `json:"color"`
}

func main() {
	matrix := Matrix{x: 100, y: 80}
	matrix.GenerateMatrix()
	matrix.GetMatrix()
	r := gin.Default()
	r.Use(cors.Default())
	r.GET("/matrix", func(c *gin.Context) {
		c.JSON(http.StatusOK, matrix.GetMatrix())
	})
	r.POST("/pixel", func(c *gin.Context) {
		var pixel Pixel
		c.BindJSON(&pixel)
		SetClickAction(1)
		c.JSON(http.StatusOK, gin.H{"status": SetPixel(pixel.X, pixel.Y, pixel.Color)})
	})
	r.GET("/sock", func(c *gin.Context) {
		handler(c.Writer, c.Request, matrix)
	})

	r.Run("localhost:5000")

}
