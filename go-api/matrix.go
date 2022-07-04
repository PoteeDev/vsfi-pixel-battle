package main

import (
	"fmt"
)

const defaultColor = "#ABABAB"

var matrixKeys []string

type Matrix struct {
	x int
	y int
}

func (m *Matrix) GenerateMatrix() {
	for i := 0; i < m.y; i++ {
		for j := 0; j < m.x; j++ {
			key := SetPixel(i, j, defaultColor)
			if key == "" {
				fmt.Println("create pixel failed on", i, j)
			} else {
				matrixKeys = append(matrixKeys, key)
			}
		}
	}
}
func (m *Matrix) GetMatrix() interface{} {
	result, err := rdb.MGet(ctx, matrixKeys...).Result()
	if err != nil {
		fmt.Println(err)
	}
	var matrix = make([][]string, m.y)
	j := -1
	for i, color := range result {
		if i%m.x == 0 {
			j++
		}
		matrix[j] = append(matrix[j], color.(string))

	}
	return matrix
}

func SetPixel(x, y int, color string) string {
	key := fmt.Sprintf("%d-%d", x, y)
	err := rdb.Set(ctx, key, color, 0).Err()
	if err == nil {
		return key
	}
	return ""
}
