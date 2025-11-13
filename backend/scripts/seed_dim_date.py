"""
Dimension Date Table Population Script
Populates dim_date table with date dimension data for data warehouse
"""
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from src.config import Base, config


class DimDate(Base):
    """Date Dimension Table"""
    __tablename__ = 'dim_date'

    date_id = Column(Integer, primary_key=True)  # Format: YYYYMMDD
    date = Column(Date, nullable=False, unique=True)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    week = Column(Integer, nullable=False)
    day_of_month = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    day_name = Column(String(10), nullable=False)
    month_name = Column(String(10), nullable=False)
    is_weekend = Column(Integer, nullable=False)  # 0=No, 1=Yes


def generate_date_range(start_date, end_date):
    """
    Generate date range for population
    Args:
        start_date: Start date (datetime)
        end_date: End date (datetime)
    Yields:
        datetime objects for each date in range
    """
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += timedelta(days=1)


def get_quarter(month):
    """Get quarter from month (1-4)"""
    return (month - 1) // 3 + 1


def populate_dim_date(start_year=2020, end_year=2030):
    """
    Populate dim_date table with date records
    Args:
        start_year: Start year (default: 2020)
        end_year: End year (default: 2030)
    """
    # Create engine and session
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create table if not exists
        Base.metadata.create_all(engine, tables=[DimDate.__table__])

        # Define date range
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)

        # Day names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']

        print(f"Populating dim_date from {start_year} to {end_year}...")

        # Batch insert
        batch_size = 1000
        records = []

        for date in generate_date_range(start_date, end_date):
            date_id = int(date.strftime('%Y%m%d'))
            year = date.year
            month = date.month
            day_of_month = date.day
            day_of_week = date.weekday()  # 0=Monday, 6=Sunday
            week = date.isocalendar()[1]
            quarter = get_quarter(month)
            is_weekend = 1 if day_of_week >= 5 else 0

            dim_date_record = DimDate(
                date_id=date_id,
                date=date.date(),
                year=year,
                quarter=quarter,
                month=month,
                week=week,
                day_of_month=day_of_month,
                day_of_week=day_of_week,
                day_name=day_names[day_of_week],
                month_name=month_names[month - 1],
                is_weekend=is_weekend
            )

            records.append(dim_date_record)

            # Batch insert
            if len(records) >= batch_size:
                session.bulk_save_objects(records)
                session.commit()
                print(f"Inserted {len(records)} records...")
                records = []

        # Insert remaining records
        if records:
            session.bulk_save_objects(records)
            session.commit()
            print(f"Inserted {len(records)} records...")

        # Get total count
        total_count = session.query(DimDate).count()
        print(f"✅ Successfully populated dim_date with {total_count} records")

    except Exception as e:
        session.rollback()
        print(f"❌ Error populating dim_date: {e}")
        raise

    finally:
        session.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Populate dim_date dimension table')
    parser.add_argument('--start-year', type=int, default=2020, help='Start year (default: 2020)')
    parser.add_argument('--end-year', type=int, default=2030, help='End year (default: 2030)')

    args = parser.parse_args()

    populate_dim_date(args.start_year, args.end_year)
