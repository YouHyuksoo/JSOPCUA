"""
Generate Sample CSV Files for Tag Import Testing

Feature 5: Database Management REST API
Generates sample_tags_1000.csv (valid data) and sample_tags_errors.csv (with errors)
"""

import pandas as pd
import random


def generate_valid_tags_csv(filename: str, count: int = 1000):
    """Generate valid tags CSV file"""
    data = []

    # Sample data
    plc_codes = ['PLC001', 'PLC002', 'PLC003']
    process_codes = ['KRCWO12ELOA101', 'KRCWO12ELOB102', 'KRCWO12ELOC103']
    divisions = ['Temperature', 'Pressure', 'Flow', 'Level', 'Speed']
    data_types = ['WORD', 'DWORD', 'BIT', 'REAL']
    units = ['°C', 'bar', 'L/min', 'mm', 'rpm', '%']

    for i in range(count):
        tag_num = i + 1
        plc_code = random.choice(plc_codes)
        process_code = random.choice(process_codes)

        data.append({
            'PLC_CODE': plc_code,
            'PROCESS_CODE': process_code,
            'TAG_ADDRESS': f'D{100 + i}',
            'TAG_NAME': f'Tag_{tag_num:04d}_{random.choice(divisions)}',
            'TAG_DIVISION': random.choice(divisions),
            'DATA_TYPE': random.choice(data_types),
            'UNIT': random.choice(units),
            'SCALE': round(random.uniform(0.1, 10.0), 2),
            'MACHINE_CODE': f'MACHINE_{random.randint(1, 10)}',
            'ENABLED': 1
        })

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✓ Generated {filename} with {count} valid tags")


def generate_error_tags_csv(filename: str):
    """Generate tags CSV with errors for testing"""
    data = [
        # Valid row
        {
            'PLC_CODE': 'PLC001',
            'PROCESS_CODE': 'KRCWO12ELOA101',
            'TAG_ADDRESS': 'D100',
            'TAG_NAME': 'Valid_Tag',
            'TAG_DIVISION': 'Temperature',
            'DATA_TYPE': 'WORD',
            'UNIT': '°C',
            'SCALE': 1.0,
            'MACHINE_CODE': 'MACHINE_1',
            'ENABLED': 1
        },
        # Invalid PLC_CODE
        {
            'PLC_CODE': 'INVALID_PLC',
            'PROCESS_CODE': 'KRCWO12ELOA101',
            'TAG_ADDRESS': 'D101',
            'TAG_NAME': 'Invalid_PLC_Code',
            'TAG_DIVISION': 'Pressure',
            'DATA_TYPE': 'WORD',
            'UNIT': 'bar',
            'SCALE': 1.0,
            'MACHINE_CODE': '',
            'ENABLED': 1
        },
        # Invalid PROCESS_CODE
        {
            'PLC_CODE': 'PLC001',
            'PROCESS_CODE': 'INVALID_PROCESS',
            'TAG_ADDRESS': 'D102',
            'TAG_NAME': 'Invalid_Process_Code',
            'TAG_DIVISION': 'Flow',
            'DATA_TYPE': 'WORD',
            'UNIT': 'L/min',
            'SCALE': 1.0,
            'MACHINE_CODE': '',
            'ENABLED': 1
        },
        # Missing TAG_NAME (empty)
        {
            'PLC_CODE': 'PLC001',
            'PROCESS_CODE': 'KRCWO12ELOA101',
            'TAG_ADDRESS': 'D103',
            'TAG_NAME': '',
            'TAG_DIVISION': 'Level',
            'DATA_TYPE': 'WORD',
            'UNIT': 'mm',
            'SCALE': 1.0,
            'MACHINE_CODE': '',
            'ENABLED': 1
        },
        # Valid row
        {
            'PLC_CODE': 'PLC002',
            'PROCESS_CODE': 'KRCWO12ELOB102',
            'TAG_ADDRESS': 'D104',
            'TAG_NAME': 'Another_Valid_Tag',
            'TAG_DIVISION': 'Speed',
            'DATA_TYPE': 'DWORD',
            'UNIT': 'rpm',
            'SCALE': 0.1,
            'MACHINE_CODE': 'MACHINE_2',
            'ENABLED': 1
        }
    ]

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"✓ Generated {filename} with 5 rows (2 valid, 3 errors)")


def main():
    """Generate both sample CSV files"""
    print("\nGenerating Sample CSV Files for Tag Import Testing")
    print("=" * 60)

    # Generate valid tags CSV (1000 rows)
    generate_valid_tags_csv('backend/data/sample_tags_1000.csv', 1000)

    # Generate error tags CSV (5 rows with errors)
    generate_error_tags_csv('backend/data/sample_tags_errors.csv')

    print("=" * 60)
    print("\nSample files generated:")
    print("  - backend/data/sample_tags_1000.csv (1000 valid tags)")
    print("  - backend/data/sample_tags_errors.csv (2 valid, 3 errors)")
    print("\nNote: Before importing, ensure corresponding PLCs and Processes exist:")
    print("  - PLC Codes: PLC001, PLC002, PLC003")
    print("  - Process Codes: KRCWO12ELOA101, KRCWO12ELOB102, KRCWO12ELOC103")


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    import os
    os.makedirs('backend/data', exist_ok=True)

    main()
