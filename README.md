# Google Cloud IP Address Ranges Microservice

This project fetches Google IP address ranges, saves them as CSV files, and uploads them to Google Cloud Storage. It is designed for deployment using Google Cloud Functions and scheduling via Cloud Scheduler.

## Table of Contents

- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Google Cloud Setup](#google-cloud-setup)
- [Deploying to Google Cloud Functions](#deploying-to-google-cloud-functions)
- [Scheduling with Cloud Scheduler](#scheduling-with-cloud-scheduler)
- [Todo: Running the Report Generator](#todo-running-the-report-generator)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Project Structure

- **main.py**: Main script that fetches IP ranges, processes them into CSV files, and uploads them to Google Cloud Storage.
- **requirements.txt**: Python dependencies.
- **README.md**: Project documentation.

## Prerequisites

- **Google Cloud Project**: Ensure billing is enabled.
- **Google Cloud SDK**: Install and configure.
- **Google Cloud Storage bucket**: Create a bucket for storing CSV files.

## Google Cloud Setup

### Important: Hardcoding Variables

Before deploying the function, make sure to hardcode the following variables in the `main.py` script:

- **`BUCKET_NAME`**: Replace the placeholder with the name of your Google Cloud Storage bucket.
- **`GOOGLE_CLOUD_PROJECT`**: Replace the placeholder with your Google Cloud project ID.

```python
# Example
BUCKET_NAME = "your-bucket-name"
GOOGLE_CLOUD_PROJECT = "your-project-id"
```

### Enable APIs & Set Up Service Account

1. Enable the following APIs in the [Google Cloud Console](https://console.cloud.google.com/):
   - **Cloud Storage API**
   - **Cloud Functions API**
   - **Cloud Scheduler API**

2. Create a Service Account in IAM & Admin.

3. Assign the **Storage Object Admin** role to the Service Account to manage objects in your Google Cloud Storage bucket.

## Deploying to Google Cloud Functions

1. **Deploy the function**:

   ```bash
   gcloud functions deploy ipAddressRangeFunction \
   --runtime python39 \
   --trigger-http \
   --allow-unauthenticated \
   --entry-point ipAddressRangeFunction
   ```

   - No need to set the `BUCKET_NAME` and `GOOGLE_CLOUD_PROJECT` as environment variables since they are hardcoded in the `main.py` script.

## Scheduling with Cloud Scheduler

1. **Create a Cloud Scheduler job**:

   ```bash
   gcloud scheduler jobs create http ip-address-range-job \
   --schedule "30 3 * * *" \
   --uri "https://REGION-PROJECT_ID.cloudfunctions.net/ipAddressRangeFunction" \
   --http-method GET \
   --oidc-service-account-email your-service-account@your-project-id.iam.gserviceaccount.com
   ```

   - Adjust the `--schedule` flag to set your desired schedule. The above example schedules the function to run daily at 3:30 AM UTC.
   - Replace `REGION` and `PROJECT_ID` with your Cloud Function's region and project ID.
   - Replace `your-service-account` and `your-project-id` with your actual service account and project ID.

## Todo: Running the Report Generator

### After 90 days of CSV data collection, you should:

1. **Run the Report Generator Script:**
   - The script will analyze the collected IP address CSV files to determine the frequency and magnitude of IP address changes over the 90-day period.

2. **Evaluate the Findings:**
   - The report will include metrics such as:
     - **Max Changes in a Day**: Identifies the maximum number of changes that occurred between any two consecutive days.
     - **Average Changes per Day**: Calculates the average number of changes across the days where changes occurred.
     - **Average Days without Changes**: Determines how frequently the IP address ranges remain unchanged.
     - **Total Changes**: Summarizes the total number of changes observed over the 90-day period.

3. **Adjust the Frequency of Updates:**
   - Depending on the report’s findings:
     - **Increase Frequency** if changes are frequent or significant, to ensure up-to-date data.
     - **Decrease Frequency** if changes are minimal or rare, to save resources and reduce unnecessary processing.

The report helps in making data-driven decisions to optimize the schedule for updating the CSV files.

## Troubleshooting

- **403 Forbidden Errors**: Ensure the service account has the correct roles, especially Storage Object Admin.
- **Other Issues**: Check the Google Cloud Functions logs for detailed error messages.

## License

MIT License
```
