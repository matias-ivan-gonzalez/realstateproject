from app import create_app

app = create_app()

def execute():
    if __name__ == '__main__':
        app.run(debug=True)

execute()