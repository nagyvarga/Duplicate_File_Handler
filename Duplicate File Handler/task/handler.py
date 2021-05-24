import os
import sys
import hashlib


def get_same_size_files(root, extension, sorting):
    list_of_directories = tuple(os.walk(root, topdown=True))
    files = {}

    for level in list_of_directories:
        for file in level[2]:
            if extension in ('', os.path.splitext(file)[1][1:]):
                path_and_filename = os.path.join(level[0], file)
                file_size = os.path.getsize(path_and_filename)
                files[path_and_filename] = file_size

    sizes = files.values()
    set_of_sizes = list(set(sizes))
    reverse_toggle = sorting == '1'  # Sorting reverse is True, if sorting is '1'
    set_of_sizes.sort(reverse=reverse_toggle)
    count_sizes = [size for size in set_of_sizes if tuple(sizes).count(size) > 1]  # File sizes that appear multiply

    # Collect duplicated files
    duplicated_files = {}
    for size in count_sizes:
        duplicated_files[size] = [key for key, value in files.items() if value == size]

    return duplicated_files


def print_same_size_files(duplicated_files):
    for duplicate_size, name_of_files in duplicated_files.items():
        print(f'\n{duplicate_size} bytes')
        for name_of_file in name_of_files:
            print(name_of_file)


def get_file_extension():
    print('\nEnter file format:')
    return input()


def get_sorting_type():
    print('\nSize sorting options:\n1. Descending\n2. Ascending')
    while True:
        print('\nEnter a sorting option:')
        sorting = input()
        if sorting in ('1', '2'):
            break
        print('\nWrong option')
    return sorting


def hashing_duplicates(duplicated_files):
    updated_duplicated_files = {}
    for duplicate_size, name_of_files in duplicated_files.items():
        # Same size of files
        files_with_hash = []
        for name_of_file in name_of_files:
            try:
                hashing_file = open(name_of_file, "rb")
            except FileNotFoundError:
                pass
            else:
                hash_for_file = hashlib.md5()
                hash_for_file.update(hashing_file.read())
                hex_hash = hash_for_file.hexdigest()
                files_with_hash.append((hex_hash, name_of_file))
                hashing_file.close()

        all_hashes_in_same_size = [hashes[0] for hashes in files_with_hash]
        unique_hash = list(set(all_hashes_in_same_size))
        final_unique_hashes = [hashes for hashes in unique_hash if all_hashes_in_same_size.count(hashes) > 1]

        final_hashes_with_filenames = {}
        for unique in final_unique_hashes:
            final_hashes_with_filenames[unique] = [filename for hashes, filename in files_with_hash if unique == hashes]

        updated_duplicated_files[duplicate_size] = final_hashes_with_filenames

    return updated_duplicated_files


def process_duplicated_files(duplicated_files):
    deletable_files = []
    num = 1
    for duplicate_size, hashes_with_files in duplicated_files.items():
        print(f'\n{duplicate_size} bytes')
        for unique_hash, name_of_files in hashes_with_files.items():
            print(f'Hash: {unique_hash}')
            for name_of_file in name_of_files:
                print(f'{num}. {name_of_file}')
                deletable_files.append((name_of_file, duplicate_size))
                num += 1
    return deletable_files


def asking_to_execute(question):
    while True:
        print(f'\n{question}')
        checking_delete = input()
        if checking_delete == 'yes':
            return True
        elif checking_delete == 'no':
            return False
        else:
            print(f'\nWrong option')


def asking_what_to_delete(numbers_of_files):
    while True:
        wrong_status = False
        print('\nEnter file numbers to delete:')
        try:
            user_choices = [int(n) for n in input().split()]
        except (ValueError, TypeError):
            wrong_status = True
        else:
            if user_choices and len(set(user_choices)) == len(user_choices) and \
                    min(user_choices) > 0 and max(user_choices) <= numbers_of_files:
                return user_choices
            else:
                wrong_status = True
        if wrong_status:
            print('\nWrong format')


def delete_files(deletable_files, file_numbers):
    freed_up_space = 0
    for num in file_numbers:
        os.remove(deletable_files[num - 1][0])
        # print(deletable_files[num - 1][0])
        freed_up_space += deletable_files[num - 1][1]
    print(f'\nTotal freed up space: {freed_up_space} bytes')


args = sys.argv

if len(args) != 2:
    print('Directory is not specified')
else:
    root_directory = args[1]
    if os.path.isdir(root_directory):
        file_format = get_file_extension()
        type_of_sorting = get_sorting_type()
        same_size_files = get_same_size_files(root_directory, file_format, type_of_sorting)
        print_same_size_files(same_size_files)
        if asking_to_execute('Check for duplicate?'):  # Checking duplicate
            hashing_unique_files = hashing_duplicates(same_size_files)
            all_deletable_files = process_duplicated_files(hashing_unique_files)
            if asking_to_execute('Delete files?'):
                choice = asking_what_to_delete(len(all_deletable_files))
                delete_files(all_deletable_files, choice)
