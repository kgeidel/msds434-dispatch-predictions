package main

import (
	"fmt"
	"net/http"
	"time"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "[%s] This will become the API for interacting w/ dispatch-predictions, check back soon!", time.Now())
	})

	http.ListenAndServe(":8080", nil)
}
