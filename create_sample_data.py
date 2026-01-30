import pandas as pd

# Create sample clothing data
clothing_data = {
    'title': ['Nike Air Max', 'Adidas Ultraboost', 'Puma RS-X'],
    'subtitle': ['Running shoes', 'Basketball', 'Sneakers'],
    'price': [120.0, 150.0, 100.0],
    'category': ['shoes', 'shoes', 'shoes']
}
df_clothing = pd.DataFrame(clothing_data)
df_clothing.to_parquet('data/clothing.parquet')
print("Created data/clothing.parquet")

# Create sample watches data
watches_data = {
    'name': ['Rolex Submariner', 'Omega Seamaster', 'Breitling Navitimer'],
    'description': ['Luxury watch', 'Sports watch', 'Aviator watch'],
    'price': [5000.0, 4500.0, 6000.0],
    'category': ['luxury', 'sports', 'aviator']
}
df_watches = pd.DataFrame(watches_data)
df_watches.to_csv('data/watches.csv', index=False)
print("Created data/watches.csv")
