def are_anagrams(str1, str2):
    # Convertir les chaînes en minuscules pour éviter les problèmes de casse
    str1 = str1.upper()
    str2 = str2.upper()

    print(str1)

    print(str2)

    # Supprimer les espaces pour comparer uniquement les caractères significatifs
    str1 = set(str1.split())
    str2 = set(str2.split())

    # Comparer les ensembles de caractères des deux chaînes
    if str2.issubset(str1):
        return True
    else: 
        return False