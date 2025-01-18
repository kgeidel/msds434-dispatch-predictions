package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

func main() {

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// System time settings
		tz, err := time.LoadLocation("America/New_York")
		if err != nil {
			log.Fatalf("failed to load timezone location: %v", err)
		}
		t := time.Now().In(tz)
		fmt.Fprintf(w, "[%s] This will become the API for interacting w/ dispatch-predictions, check back soon!", t.Format("2006-01-02 15:04:05 MST"))
	})
	fmt.Printf("Listening on port 8080...\n	")
	http.ListenAndServe(":8080", nil)
}
