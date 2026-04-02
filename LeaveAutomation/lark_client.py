import re
from datetime import datetime
import requests
import config


class LarkClient:
    BASE_URL = "https://open.larksuite.com/open-apis"

    def __init__(self):
        self.tenant_token = None
        self.spreadsheet_token = None
        self.sheet_id = None

    def authenticate(self):
        """Get tenant_access_token from Lark Open API."""
        resp = requests.post(
            f"{self.BASE_URL}/auth/v3/tenant_access_token/internal",
            json={
                "app_id": config.LARK_APP_ID,
                "app_secret": config.LARK_APP_SECRET,
            },
        )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Lark auth failed: {data.get('msg', 'Unknown error')}")
        self.tenant_token = data["tenant_access_token"]
        return self.tenant_token

    def _headers(self):
        if not self.tenant_token:
            self.authenticate()
        return {
            "Authorization": f"Bearer {self.tenant_token}",
            "Content-Type": "application/json",
        }

    def resolve_wiki_url(self):
        """Extract the spreadsheet token from the wiki page URL.

        The wiki URL token can be used directly as the spreadsheet token
        (no wiki:wiki scope needed).
        """
        m = re.search(r"/wiki/(\w+)", config.LARK_WIKI_URL)
        if not m:
            raise ValueError(f"Cannot parse wiki URL: {config.LARK_WIKI_URL}")

        # The wiki node token works directly as the spreadsheet token
        self.spreadsheet_token = m.group(1)

        return self.spreadsheet_token

    def get_sheets(self):
        """Get all sheets in the spreadsheet."""
        if not self.spreadsheet_token:
            self.resolve_wiki_url()

        resp = requests.get(
            f"{self.BASE_URL}/sheets/v3/spreadsheets/{self.spreadsheet_token}/sheets/query",
            headers=self._headers(),
        )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Get sheets failed: {data.get('msg')}")

        sheets = data.get("data", {}).get("sheets", [])
        return sheets

    def set_sheet(self, sheet_id):
        """Set the active sheet to work with."""
        self.sheet_id = sheet_id

    def read_range(self, range_str):
        """Read a range of cells from the spreadsheet.

        Args:
            range_str: e.g. "Sheet1!A1:Z100" or just "A1:Z100" (uses self.sheet_id)
        """
        if not self.spreadsheet_token:
            self.resolve_wiki_url()

        if "!" not in range_str and self.sheet_id:
            range_str = f"{self.sheet_id}!{range_str}"

        resp = requests.get(
            f"{self.BASE_URL}/sheets/v2/spreadsheets/{self.spreadsheet_token}/values/{range_str}",
            headers=self._headers(),
        )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Read range failed: {data.get('msg')}")

        return data.get("data", {}).get("valueRange", {}).get("values", [])

    def write_cell(self, range_str, value):
        """Write a value to a specific cell or range.

        Args:
            range_str: e.g. "Sheet1!AF5" or just "AF5" (uses self.sheet_id)
            value: the value to write
        """
        if not self.spreadsheet_token:
            self.resolve_wiki_url()

        if "!" not in range_str and self.sheet_id:
            range_str = f"{self.sheet_id}!{range_str}"

        # Lark requires range format "SHEET!A1:A1" (not just "SHEET!A1")
        if ":" not in range_str:
            range_str = f"{range_str}:{range_str.split('!')[-1]}"

        resp = requests.put(
            f"{self.BASE_URL}/sheets/v2/spreadsheets/{self.spreadsheet_token}/values",
            headers=self._headers(),
            json={
                "valueRange": {
                    "range": range_str,
                    "values": [[value]],
                }
            },
        )
        data = resp.json()
        if data.get("code") != 0:
            raise RuntimeError(f"Write cell failed: {data.get('msg')}")

        return True

    def find_employee_row(self, employee_name):
        """Find the row number for an employee by name (column G).

        Returns (row_number, row_data) or (None, None) if not found.
        """
        # Read column G (Employee Name) in batches
        batch_size = 200
        for start_row in range(2, 2000, batch_size):
            end_row = start_row + batch_size - 1
            try:
                values = self.read_range(f"G{start_row}:G{end_row}")
            except RuntimeError:
                break

            if not values:
                break

            for i, row in enumerate(values):
                if row and len(row) > 0:
                    cell_val = str(row[0]).strip().lower()
                    if cell_val == employee_name.strip().lower():
                        return start_row + i, row

        return None, None

    def find_date_column(self, target_date):
        """Find the column letter(s) for a specific date in the header row.

        Date headers are stored as Excel serial numbers (days since 1899-12-30)
        starting from column AF.

        Returns column letter(s) or None.
        """
        try:
            values = self.read_range("AF1:BZ1")
        except RuntimeError:
            return None

        if not values or not values[0]:
            return None

        # Convert target_date to Excel serial number for comparison
        from datetime import datetime
        excel_epoch = datetime(1899, 12, 30).date()
        target_serial = (target_date - excel_epoch).days

        for i, cell in enumerate(values[0]):
            if cell is None:
                continue

            # Handle serial number dates (int or float > 40000)
            try:
                serial = int(float(cell))
                if serial > 40000 and serial == target_serial:
                    return _col_index_to_letter(31 + i)  # AF = index 31
            except (ValueError, TypeError):
                pass

            # Fallback: try parsing as formatted date string
            cell_str = str(cell).strip()
            try:
                from dateutil import parser as dp
                cell_date = dp.parse(cell_str, fuzzy=True, dayfirst=True).date()
                if cell_date == target_date:
                    return _col_index_to_letter(31 + i)
            except (ValueError, OverflowError):
                continue

        return None

    def auto_select_sheet(self, target_date):
        """Automatically select the correct monthly sheet for a given date.

        Sheets are named: Jan, Feb, Mar, ... Dec
        """
        month_name = target_date.strftime("%b")  # "Jan", "Feb", etc.
        sheets = self.get_sheets()
        for s in sheets:
            if s.get("title", "").strip().lower() == month_name.lower():
                self.set_sheet(s["sheet_id"])
                return s
        raise ValueError(f"No sheet found for month: {month_name}")

    def write_leave(self, employee_name, target_date, leave_type):
        """Write a leave type to the sheet for an employee on a specific date.

        Auto-selects the correct monthly sheet if not already set.
        Returns True on success, raises on failure.
        """
        # Auto-select the monthly sheet for this date
        self.auto_select_sheet(target_date)

        row_num, _ = self.find_employee_row(employee_name)
        if row_num is None:
            raise ValueError(f"Employee '{employee_name}' not found in sheet")

        col = self.find_date_column(target_date)
        if col is None:
            raise ValueError(
                f"Date column for {target_date.strftime('%d-%b')} not found in sheet"
            )

        cell_ref = f"{col}{row_num}"
        self.write_cell(cell_ref, leave_type)
        return True


def _col_index_to_letter(index):
    """Convert 0-based column index to Excel-style column letter(s).

    0 -> A, 25 -> Z, 26 -> AA, etc.
    """
    result = ""
    while index >= 0:
        result = chr(65 + index % 26) + result
        index = index // 26 - 1
    return result
