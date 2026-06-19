from app import app, ensure_storage_exists

if __name__ == "__main__":
    ensure_storage_exists()
    app.run(debug=True)
