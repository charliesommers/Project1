"""
VSIN Web Scraper
Automatically fetches Greg Peterson's daily CBB lines from VSIN
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from typing import Optional, List, Dict
import os


class VSINScraper:
    """Scrapes Greg Peterson's daily lines from VSIN website."""

    def __init__(self):
        """Initialize VSIN scraper."""
        self.base_url = "https://vsin.com/college-basketball/greg-petersons-daily-college-basketball-lines/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_daily_lines(self, save_path: Optional[str] = None) -> Optional[str]:
        """
        Fetch Greg's daily lines from VSIN.

        Args:
            save_path: Optional path to save the Excel file

        Returns:
            Path to saved file or None if failed
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for Excel/spreadsheet download link
            # The exact selector may need adjustment based on VSIN's page structure
            excel_link = self._find_excel_link(soup)

            if excel_link:
                return self._download_excel(excel_link, save_path)
            else:
                # Try to parse data from HTML table if available
                print("No direct Excel link found. Attempting to parse HTML...")
                return self._parse_html_table(soup, save_path)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching from VSIN: {e}")
            return None

    def _find_excel_link(self, soup: BeautifulSoup) -> Optional[str]:
        """Find Excel download link in the page."""
        # Look for links containing .xlsx, .xls, or Excel-related text
        links = soup.find_all('a', href=True)

        for link in links:
            href = link.get('href', '')
            text = link.get_text().lower()

            if '.xlsx' in href or '.xls' in href:
                return href
            if 'download' in text and 'spreadsheet' in text:
                return href
            if 'excel' in text:
                return href

        return None

    def _download_excel(self, url: str, save_path: Optional[str] = None) -> Optional[str]:
        """Download Excel file from URL."""
        try:
            # Make URL absolute if relative
            if not url.startswith('http'):
                if url.startswith('/'):
                    url = f"https://vsin.com{url}"
                else:
                    url = f"https://vsin.com/{url}"

            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Determine save path
            if not save_path:
                today = datetime.now().strftime('%Y%m%d')
                save_path = f"data/gregs_lines_{today}.xlsx"

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save file
            with open(save_path, 'wb') as f:
                f.write(response.content)

            print(f"Downloaded Greg's lines to: {save_path}")
            return save_path

        except Exception as e:
            print(f"Error downloading Excel file: {e}")
            return None

    def _parse_html_table(self, soup: BeautifulSoup, save_path: Optional[str] = None) -> Optional[str]:
        """
        Parse lines from HTML table if Excel not available.

        Args:
            soup: BeautifulSoup object
            save_path: Path to save parsed data

        Returns:
            Path to saved file or None
        """
        try:
            # Find tables in the page
            tables = soup.find_all('table')

            if not tables:
                print("No tables found on page")
                return None

            # Try to parse the most relevant table
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) < 2:
                    continue

                # Extract data
                data = []
                headers = []

                # Get headers
                header_row = rows[0]
                headers = [th.get_text().strip() for th in header_row.find_all(['th', 'td'])]

                # Get data rows
                for row in rows[1:]:
                    cells = [td.get_text().strip() for td in row.find_all('td')]
                    if cells:
                        data.append(cells)

                if data:
                    # Create DataFrame
                    df = pd.DataFrame(data, columns=headers if headers else None)

                    # Save to Excel
                    if not save_path:
                        today = datetime.now().strftime('%Y%m%d')
                        save_path = f"data/gregs_lines_{today}.xlsx"

                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    df.to_excel(save_path, index=False, engine='openpyxl')

                    print(f"Parsed and saved Greg's lines to: {save_path}")
                    return save_path

            print("Could not parse data from HTML")
            return None

        except Exception as e:
            print(f"Error parsing HTML table: {e}")
            return None

    def get_latest_lines_path(self) -> Optional[str]:
        """
        Get path to most recently downloaded lines file.

        Returns:
            Path to latest file or None
        """
        data_dir = "data"
        if not os.path.exists(data_dir):
            return None

        # Find all Greg's lines files
        files = [f for f in os.listdir(data_dir) if f.startswith('gregs_lines_') and f.endswith('.xlsx')]

        if not files:
            return None

        # Sort by modification time (most recent first)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(data_dir, x)), reverse=True)

        return os.path.join(data_dir, files[0])

    def auto_update_check(self) -> bool:
        """
        Check if we need to download new lines.

        Returns:
            True if update needed, False otherwise
        """
        latest_file = self.get_latest_lines_path()

        if not latest_file:
            return True

        # Check if file is from today
        file_mtime = os.path.getmtime(latest_file)
        file_date = datetime.fromtimestamp(file_mtime).date()
        today = datetime.now().date()

        return file_date < today
