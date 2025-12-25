"""
Database seeding script.
Seeds the database with mock designs from the notebook.
"""
from app.database import SessionLocal
from app.models import Design
from app.utils.constants import DESIGN_DATABASE


def seed_designs():
    """Seed designs from notebook's DESIGN_DATABASE."""
    db = SessionLocal()
    
    try:
        # Check if designs already exist
        existing_count = db.query(Design).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} designs. Skipping seed.")
            return
        
        # Seed designs from notebook
        for design_id, attributes in DESIGN_DATABASE.items():
            design = Design(
                id=design_id,
                **attributes
            )
            db.add(design)
        
        db.commit()
        print(f" Seeded {len(DESIGN_DATABASE)} designs from notebook")
        
        # Display seeded designs
        for design_id in DESIGN_DATABASE.keys():
            print(f"   - {design_id}")
    
    except Exception as e:
        print(f" Error seeding database: {e}")
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding database with designs from notebook...")
    seed_designs()
