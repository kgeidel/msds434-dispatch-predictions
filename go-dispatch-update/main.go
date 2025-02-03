package main

////////////////////////////////////////////////////////
// Kevin Geidel
// MSDS 434 - Section 55 - Winter '25
// dispatch-predictions - main.go
//
// Go based package that keeps the hfddc database
// up-to-date with the latest incident records.
////////////////////////////////////////////////////////

import (
	"context"
	"database/sql"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/signal"
	"time"

	_ "github.com/microsoft/go-mssqldb"
)

var (
	api_host       = "3.139.234.43"
	api_port       = "8000"
	token_filepath = "../.token"
	db_name        = "REDNMX"
)

// For parsing the API response containing filter date
type DateResponse struct {
	Dtg    string `json:"most_recent_incident"`
	Detail string `json:"detail"`
}

// A struct to contain an individual incident record
type Incident struct {
	Num           string `json:"num"`
	Dtg_alarm     string `json:"dtg_alarm"`
	Fd_id         string `json:"fd_id"`
	Street_number string `json:"street_number"`
	Route         string `json:"route"`
	Suite         string `json:"suite"`
	Postal_code   string `json:"postal_code"`
	Call_duration string `json:"duration"`
	Type_str      string `json:"type_str"`
}

func main() {
	incidents := get_incident_records()

}

func get_incident_records() []Incident {
	// M$ SQL Server
	// Establish context
	ctx, stop := context.WithCancel(context.Background())
	defer stop()
	appSignal := make(chan os.Signal, 3)
	signal.Notify(appSignal, os.Interrupt)
	go func() {
		<-appSignal
		stop()
	}()
	REDALERT_DB_HOST, ok := os.LookupEnv("REDALERT_DB_HOST")
	if !ok {
		fmt.Println("REDALERT_DB_HOST is not set")
	}
	REDALERT_DB_USER, ok := os.LookupEnv("REDALERT_DB_USER")
	if !ok {
		fmt.Println("REDALERT_DB_USER is not set")
	}
	REDALERT_DB_PASSWORD, ok := os.LookupEnv("REDALERT_DB_PASSWORD")
	if !ok {
		fmt.Println("REDALERT_DB_PASSWORD is not set")
	}
	dsn := fmt.Sprintf("sqlserver://%s:%s@%s:1433?database=%s", REDALERT_DB_USER, REDALERT_DB_PASSWORD, REDALERT_DB_HOST, db_name)
	db, err := sql.Open("sqlserver", dsn)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
	db.SetConnMaxLifetime(0)
	db.SetMaxIdleConns(3)
	db.SetMaxOpenConns(3)

	// Open connection
	OpenDbConnection(ctx, db)

	// Make the query
	timeout, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	rows, err := db.QueryContext(timeout, get_qstr())
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()
	// process the results
	var incidents []Incident
	for rows.Next() {
		var incident Incident
		err = rows.Scan(
			&incident.Num,
			&incident.Dtg_alarm,
			&incident.Fd_id,
			&incident.Street_number,
			&incident.Route,
			&incident.Suite,
			&incident.Postal_code,
			&incident.Call_duration,
			&incident.Type_str,
		)
		if err != nil {
			log.Fatal(err)
		}
		// add the record to the slice of incidents
		incidents = append(incidents, incident)
	}
	err = rows.Err()
	if err != nil {
		log.Fatal(err)
	}
	return incidents
}

// Connect to the M$ SQL Server
func OpenDbConnection(ctx context.Context, db *sql.DB) {
	ctx, cancel := context.WithTimeout(ctx, 1*time.Second)
	defer cancel()
	if err := db.PingContext(ctx); err != nil {
		log.Fatal("Unable to connect to database: %v", err)
	}
}

// Fetch the REDNMX qstr
func get_qstr() string {
	qstr := fmt.Sprintf(`select
	COALESCE(INCNUM, '') as num, 
	COALESCE(DATETIMEALARM, '') as dtg_alarm,
	COALESCE(FDID, '') as fd_id,
	COALESCE(STRNUM, '') as street_number,
	COALESCE(STREET, '') as route,
	COALESCE(ROOMAPT, '') as suite,
	COALESCE(ZIP, '') as postal_code,
	COALESCE(EVLENGTH, 0) as call_duration,
	COALESCE(n5inctype.DESCR, '') as type_str		
from
	dbo.nfirsmain
	JOIN dbo.n5inctype on nfirsmain.SITFOUND=code
where
	DATETIMEALARM >= '%s';
	`, get_filter_date())
	return qstr
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
