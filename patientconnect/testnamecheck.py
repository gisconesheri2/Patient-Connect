names = 'peter gikonyo gaceri'
n = 'gaceri gikonyo peter'
users = ['Dr JOEL RICHARD WAMBWA', 'Prof KIHUMBU THAIRU', 'Dr JOSEPH AMOLO ALUOCH']
def check_name(name1, name2):
    if len(name1) == len(name2):
        x = 1
        names = name1.split()
        for name in names:
            if name in name2:
                if x == len(names):
                    return True
                x += 1
            else:
                return False
    return False

ui = 'kihumbu thairu'
user_found = False
for user in users:
    cleaned_name = user.lower().replace('dr ', '').replace('prof ', '')
    if check_name(cleaned_name, ui) == True:
        user_found = user
        break
print(user_found)