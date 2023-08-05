Convert spelled numbers such as 'one thousand, two hundred and thirty-three' or 
'one thousand two hundred thirty three' to their equivalent forms in digits 
(1233). 

Handles British-style "and" as well as US versions without "and", and 
accepts commas and hyphens in appropriate positions (although they are never 
compulsory)

    >>> spelled_num_to_digits("one")
    1
    >>> spelled_num_to_digits("twelve")
    12
    >>> spelled_num_to_digits("seventy-two")
    72
    >>> spelled_num_to_digits("Three hundred")
    300
    >>> spelled_num_to_digits("TWELVE HUNDRED")
    1200
    >>> spelled_num_to_digits("twelve thousand three hundred four")
    12304
    >>> spelled_num_to_digits("twelve thousand, five hundred and six")
    12506
    >>> spelled_num_to_digits("six   Million")
    6000000
    >>> spelled_num_to_digits("six million four hundred thousand five")
    6400005
    >>> spelled_num_to_digits(
    ...   'one hundred twenty three billion, four hundred fifty six million, '
    ...   'seven hundred eighty nine thousand twelve')
    123456789012
    >>> spelled_num_to_digits("four decillion")
    4000000000000000000000000000000000L


    >>> replace_spelled_numbers('There are TEN sponges')
    'There are 10 sponges'
    >>> replace_spelled_numbers('I got ninety nine problems')
    'I got 99 problems'
    >>> replace_spelled_numbers('He got two million, one hundred and '
    ...   'eighty-two thousand, three hundred and twenty five problems')
    'He got 2182325 problems'
    >>> replace_spelled_numbers('I have five coconuts and two hundred '
    ...   'thirty three carrots')
    'I have 5 coconuts and 233 carrots'


Adapted and extended from https://github.com/ghewgill/text2num
