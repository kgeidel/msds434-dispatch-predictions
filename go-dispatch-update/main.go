package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

var (
	api_host       = "3.145.111.239"
	api_port       = "8000"
	token_filepath = "../.token"
)

// For parsing the API response containing filter date
type DateResponse struct {
	Dtg    string `json:"most_recent_incident"`
	Detail string `json:"detail"`
}

func main() {
	date_str := get_filter_date()
	fmt.Println(date_str)
}

// Return a string representation of the date to use when querying call db
func get_filter_date() string {
	endpoint_url := "http://" + api_host + ":" + api_port + "/api/calls/get_sync_filters/"
	client := http.Client{Timeout: 5 * time.Second}
	request, err := http.NewRequest(http.MethodGet, endpoint_url, nil)
	if err != nil {
		log.Fatalf("Error creating request: %v", err)
	}
	// Set the Authorization header with the bearer token
	request.Header.Set("Authorization", get_api_auth_str())
	// Send the request
	response, err := client.Do(request)
	if err != nil {
		log.Fatalf("Error sending request: %v", err)
	}
	defer response.Body.Close()
	// Read the response body
	body, err := io.ReadAll(response.Body)
	if err != nil {
		log.Fatalf("Error reading response body: %v", err)
	}

	// Unmarshal the JSON data into the struct
	var dateresponse DateResponse
	err = json.Unmarshal([]byte(body), &dateresponse)
	if err != nil {
		log.Fatalf("Error parsing response json: %v", err)
	}
	if dateresponse.Dtg == "" {
		log.Fatalf("Expected dtg str, got empty str. API response: {detail: %v}", dateresponse.Detail)
	}
	return dateresponse.Dtg[:10]
}

// Extract the API web token value from the .token file
func get_api_auth_str() string {
	content, err := os.ReadFile(token_filepath)
	if err != nil {
		log.Fatal(err)
	}
	return string(content)
}
