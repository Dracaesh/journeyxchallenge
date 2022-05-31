import re
import json
import socket
from socket import gaierror
from urllib.request import Request, urlopen


# Placeholder function for if we ever want to work on the CURRENT WORD in the future
def deal_with_words(dict, word):
    pass


# Adds @mentions to the result dictionary
def add_mention(dict, word):
    # This assumes proper spacing for mentions; if we cannot assume that a whitespace character is the ending character,
    # we could add regex logic here to doublecheck the word as we did in the 'add_emoji' function
    (dict.get("mentions")).append(word[1:])
    dict["words"] -= 1


# Add links/urls to the result dictionary
def add_link(dict, word):
    # As per the prompt, we assume a string starting with 'http' is a valid URL. We could implement try/catch handling
    # here to account for invalid URLs in the future.
    if 'http' == word[0:4]:
        req = Request(word, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = urlopen(req).read().decode('utf-8')
        title = re.findall('<title>(.+?)</title', webpage)
        dict["links"].append({"url": word, "title": title[0]})
        dict["words"] -= 1


# Adds emojis to the result dictionary
def add_emoji(dict, word):
    # If the word we see doesn't follow emoji guidelines, we instead consider it a regular word (aka ignoring it)
    if (re.match(r"\((\S*)\)", word)) and len(word) <= 15:
        (dict.get("emoticons")).append(word[1:-1])
        dict["words"] -= 1


# "Main" function that handles determination of word types and produces/prints a JSON string of the results
def take_msg(msg, file):
    mentions = []
    links = []
    emojis = []
    wordlist = msg.split()
    words = len(wordlist)

    # Switch-case dict for handling the first character of the word we're looking at currently
    identifier = {
        '@': add_mention,
        'h': add_link,
        '(': add_emoji
    }

    result = {
        "emoticons": emojis,
        "mentions": mentions,
        "links": links,
        "words": words
    }
    # We loop through the possible 'words' in the given input and determine which function to use based on the first
    # character of the word we are looking at
    for statement in range(len(wordlist)):
        # Default to 'deal_with_words' function for regular words
        decision = identifier.get(wordlist[statement][0], deal_with_words)
        decision(result, wordlist[statement])

    json_result = json.dumps(result, indent=4)
    file.write(json_result + '\n\n')
    print(json_result)


# To test on other messages, place input strings in the following 'message_list' list
message_list = ['@john hey, you around?', 'The World Series is starting soon! (cheer) https://www.mlb.com/ and '
                                          'https://espn.com', '@mary @john (success) such a cool feature! Check this '
                                                              'out: ''https://journyx.com/features-and-benefits/data'
                                                              '-validation-tool']

f = open("JSON_output.txt", "a")
f.truncate(0)

for message in range(len(message_list)):
    take_msg(message_list[message], f)

f.close()
