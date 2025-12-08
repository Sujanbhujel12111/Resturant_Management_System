import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
try:
    import django
    django.setup()
except Exception as e:
    print("Failed to setup Django. Are you running this from the project root and is DJANGO_SETTINGS_MODULE correct?")
    raise

from django.contrib.auth import get_user_model
import argparse
import getpass

User = get_user_model()

def create_superuser(username, email, password):
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists. No changes made.")
        return 0
    try:
        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"Created superuser '{username}'.")
        except TypeError:
            # Fallback for custom user models
            user = User(username=username, email=email, is_staff=True, is_superuser=True)
            user.set_password(password)
            user.save()
            print(f"Created superuser '{username}' (fallback).")
        return 0
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return 1

def parse_args():
    parser = argparse.ArgumentParser(description="Create a Django superuser (non-interactive or interactive).")
    parser.add_argument('--username', '-u', help='Username', default=os.environ.get('SUPERUSER_USERNAME', 'admin'))
    parser.add_argument('--email', '-e', help='Email', default=os.environ.get('SUPERUSER_EMAIL', 'admin@example.com'))
    parser.add_argument('--password', '-p', help='Password (use with care)', default=os.environ.get('SUPERUSER_PASSWORD'))
    parser.add_argument('--no-input', action='store_true', dest='noinput', help='Do not prompt for missing fields')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    username = args.username
    email = args.email
    password = args.password

    if not password and not args.noinput:
        # prompt interactively if password not provided and not no-input
        try:
            password = getpass.getpass(f"Password for {username}: ")
            password2 = getpass.getpass("Confirm password: ")
            if password != password2:
                print("Passwords do not match.")
                sys.exit(1)
        except Exception as e:
            print(f"Failed to read password: {e}")
            sys.exit(1)

    if args.noinput and not password:
        print("Non-interactive mode requires --password or SUPERUSER_PASSWORD env var.")
        sys.exit(1)

    exit_code = create_superuser(username=username, email=email, password=password)
    sys.exit(exit_code)
