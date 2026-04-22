from database import SessionLocal, engine
import models
import random

# Create tables if not exist
models.Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    # Check if we already seeded
    if db.query(models.Property).first():
        print("Database already seeded.")
        db.close()
        return

    cities = ['Bangalore', 'Mumbai', 'New Delhi', 'Bhubaneshwar', 'Hyderabad']
    types = ['Rent', 'Buy']
    property_types = ['flat', 'house']
    
    adjectives = ['Luxurious', 'Spacious', 'Cozy', 'Modern', 'Elegant', 'Affordable', 'Premium', 'Beautiful']
    
    properties = []
    for city in cities:
        for i in range(10):
            t = random.choice(types)
            pt = random.choice(property_types)
            beds = random.randint(1, 5)
            baths = random.randint(1, beds + 1)
            area = random.randint(500, 4000)
            
            if t == 'Rent':
                price = random.randint(10000, 100000)
            else:
                price = random.randint(3000000, 50000000)
                
            title = f"{random.choice(adjectives)} {beds} BHK {pt.capitalize()} in {city}"
            description = f"A wonderful {beds} bedroom {pt} located in the heart of {city}. It offers great amenities and a comfortable living space of {area} sqft."
            
            # Using realistic unspash IDs for properties
            real_estate_images = [
                "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
                "https://images.unsplash.com/photo-1512917774080-9991f1c4c750",
                "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9",
                "https://images.unsplash.com/photo-1600607687920-4e2a09be1587",
                "https://images.unsplash.com/photo-1518780664697-55e3ad937233",
                "https://images.unsplash.com/photo-1484154218962-a197022b5858",
                "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
                "https://images.unsplash.com/photo-1600607687644-c7171b42498f",
                "https://images.unsplash.com/photo-1600566753086-00f18efc2291",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2"
            ]
            
            image_url = f"{random.choice(real_estate_images)}?auto=format&fit=crop&w=800&q=80"
            
            prop = models.Property(
                title=title,
                description=description,
                city=city,
                price=price,
                type=t,
                property_type=pt,
                bedrooms=beds,
                bathrooms=baths,
                area_sqft=area,
                image_url=image_url
            )
            properties.append(prop)
            
    db.add_all(properties)
    db.commit()
    db.close()
    print("Database seeded with 50 properties.")

if __name__ == '__main__':
    seed_db()
