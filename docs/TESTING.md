# Testing

Required checks after installing Python 3.12+ dependencies:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
pytest
```

The current environment has Python 3.7 and no Django installation, so checks cannot be executed here yet.
