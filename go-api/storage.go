package main

import (
	"context"
	"fmt"

	"github.com/go-redis/redis/v8"
)

var ctx = context.Background()
var rdb = redis.NewClient(&redis.Options{
	Addr:     "redis:6379",
	Password: "", // no password set
	DB:       0,  // use default DB
})

func SetClickAction(value int) error {
	return rdb.Set(ctx, "click", value, 0).Err()
}

func GetClickAction() string {
	result, err := rdb.Get(ctx, "click").Result()
	if err != nil {
		fmt.Println(err)
		return "0"
	}
	return result
}
