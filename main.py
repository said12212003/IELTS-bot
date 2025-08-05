from sections import reading, listening, writing, speaking


def show_menu():
    print("\n📘 Welcome to IELTS Console Prep")
    print("Please choose a section:")
    print("1. Reading")
    print("2. Listening")
    print("3. Writing")
    print("4. Speaking")
    print("5. Exit")


def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1–5): ").strip()

        if choice == '1':
            reading.start()
        elif choice == '2':
            listening.start()
        elif choice == '3':
            writing.start()
        elif choice == '4':
            speaking.start()
        elif choice == '5':
            print("Good luck with your IELTS preparation!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
