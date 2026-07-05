import os
import sys
import pandas as pd
from database import DatabaseManager


def clean_list(val):
    if pd.isna(val) or not str(val).strip() or str(val).lower() == 'nan':
        return []
    return [s.strip() for s in str(val).split(",") if s.strip()]


def main():
    print("=" * 50)
    print("InternHunt Demo Database Seeder")
    print("=" * 50)

    # Verify CSV exists
    csv_file = "candidate_registry_master.csv"
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file '{csv_file}' could not be found.")
        print("Please place the file in the root directory and try again.")
        sys.exit(1)

    # Initialize database
    try:
        db = DatabaseManager()
        if db.connection is None:
            print("❌ Error: Could not connect to the Neon database.")
            print("Please verify your DATABASE_URL environment variable in .env.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: Database initialization failed: {e}")
        sys.exit(1)

    print("Connected to Neon Database")

    # Read CSV
    try:
        df = pd.read_csv(csv_file)
        total_rows = len(df)
        print(f"Loaded {total_rows} candidates")
    except Exception as e:
        print(f"❌ Error: Failed to read CSV file: {e}")
        sys.exit(1)

    print("Importing...")
    
    imported = 0
    failed = 0

    # Insert each candidate
    for idx, row in df.iterrows():
        row_num = idx + 1
        try:
            # Parse & cast fields safely
            res_score = int(row["Resume Score"]) if pd.notna(row["Resume Score"]) else 0
            no_of_pages = int(row["Pages"]) if pd.notna(row["Pages"]) else 1
            
            success = db.insert_user_data(
                name=str(row["Name"]) if pd.notna(row["Name"]) else "Unknown",
                email=str(row["Email"]) if pd.notna(row["Email"]) else "unknown@example.com",
                res_score=res_score,
                timestamp=str(row["Timestamp"]) if pd.notna(row["Timestamp"]) else "",
                no_of_pages=no_of_pages,
                reco_field=str(row["Predicted Field"]) if pd.notna(row["Predicted Field"]) else "General",
                cand_level=str(row["User Level"]) if pd.notna(row["User Level"]) else "Beginner",
                skills=clean_list(row["Skills"]),
                recommended_skills=clean_list(row["Recommended Skills"]),
                courses=clean_list(row["Courses"])
            )

            if success:
                imported += 1
            else:
                failed += 1
                print(f"Row {row_num} failed: Database insert returned False")
                
        except Exception as row_ex:
            failed += 1
            print(f"Row {row_num} failed: {row_ex}")

        # Print progress output
        print(f"[{row_num}/{total_rows}]")

    print("Finished")
    print(f"Imported: {imported}")
    print(f"Failed: {failed}")

    # Close connection
    try:
        db.close()
    except Exception as close_ex:
        print(f"Warning: Error closing database connection: {close_ex}")


if __name__ == "__main__":
    main()
