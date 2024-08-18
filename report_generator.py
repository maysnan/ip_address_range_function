import os
import csv
from datetime import datetime
from google.cloud import storage

class GCSClient:
    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def list_files(self, folder):
        blobs = list(self.client.list_blobs(self.bucket, prefix=folder))
        return sorted([blob.name for blob in blobs if blob.name.endswith('.csv')])

    def count_files(self, folder):
        return len(self.list_files(folder))

    def read_csv_as_set(self, blob_name):
        blob = self.bucket.blob(blob_name)
        content = blob.download_as_text()
        return set(content.strip().splitlines())

    def upload_report(self, report_filename, folder):
        blob = self.bucket.blob(f"{folder}{os.path.basename(report_filename)}")
        blob.upload_from_filename(report_filename)
        print(f"Uploaded report to {folder}")

class IPAddressRangeReport:
    def __init__(self, gcs_client, folder):
        self.gcs_client = gcs_client
        self.folder = folder
        self.files = self.gcs_client.list_files(folder)
        self.max_changes = 0
        self.total_changes = 0
        self.days_with_no_change = 0
        self.changes_per_day = []

    def calculate_differences(self, ip_list1, ip_list2):
        added_ips = ip_list2 - ip_list1
        removed_ips = ip_list1 - ip_list2
        return added_ips, removed_ips

    def process_files(self):
        for i in range(1, len(self.files)):
            current_file = self.files[i]
            previous_file = self.files[i-1]

            current_ips = self.gcs_client.read_csv_as_set(current_file)
            previous_ips = self.gcs_client.read_csv_as_set(previous_file)

            added_ips, removed_ips = self.calculate_differences(previous_ips, current_ips)
            changes_count = len(added_ips) + len(removed_ips)

            if changes_count == 0:
                self.days_with_no_change += 1
            else:
                self.changes_per_day.append(changes_count)
                self.total_changes += changes_count
                if changes_count > self.max_changes:
                    self.max_changes = changes_count

    def generate_report(self):
        if len(self.files) < 90:
            print(f"Not enough files to generate a report for {self.folder}")
            return

        self.process_files()

        avg_changes_per_day = (self.total_changes / len(self.changes_per_day)) if self.changes_per_day else 0
        avg_days_without_change = self.days_with_no_change / 90

        report_filename = f"{self.folder}report_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(report_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Max Changes in a Day', self.max_changes])
            writer.writerow(['Avg Changes per Day', avg_changes_per_day])
            writer.writerow(['Avg Days without Changes', avg_days_without_change])
            writer.writerow(['Total Changes', self.total_changes])
            writer.writerow(['Total Days with Changes', len(self.changes_per_day)])

        print(f"Report generated: {report_filename}")
        self.gcs_client.upload_report(report_filename, self.folder)

class ReportGenerator:
    def __init__(self, gcs_client):
        self.gcs_client = gcs_client

    def generate_reports_for_folders(self, folders):
        for folder in folders:
            if self.gcs_client.count_files(folder) >= 90:
                report = IPAddressRangeReport(self.gcs_client, folder)
                report.generate_report()

def main():
    bucket_name = os.environ.get('BUCKET_NAME')
    gcs_client = GCSClient(bucket_name)

    folders = [
        "google_ip_address_ranges/logs/ipv4s/",
        "google_ip_address_ranges/logs/ipv6s/"
    ]

    report_generator = ReportGenerator(gcs_client)
    report_generator.generate_reports_for_folders(folders)

if __name__ == "__main__":
    main()
