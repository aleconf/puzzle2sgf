#!/usr/bin/python
import re
import requests
import os
import time


puzzle_n = "a"
flag = 404
while not (puzzle_n.isdigit() and flag == 200):
    # while flag != 200:
    puzzle_n = input(
        "Please insert the puzzle number, i.e. the puzzle id taken from "
        + "the puzzle URL: ",
    )
    check_validity = requests.get("https://online-go.com/puzzle/" + puzzle_n)
    flag = check_validity.status_code
print("\n")

coll = "0"
while coll not in ["1", "2"]:
    coll = input(
        "Would you like to download only the specified puzzle (1) or all "
        + "problems of the specified puzzle's collection (2)? Please, "
        + "answer only with 1 or 2. \n",
    )
print("\n")

auth_answer = "0"
while auth_answer not in ["y", "n"]:
    auth_answer = input(
        "Would you like to authenticate yourself so you could download "
        + 'private problems? Please, answer only with "y" or "n". \n'
    )
print("\n")

if coll == "1":
    downloadWholeCollection = False
else:
    downloadWholeCollection = True

# puzzleNumber = 6544
puzzleNumber = int(puzzle_n)

skipAuthentication = True
if auth_answer == "y":
    skipAuthentication = False


def escape(text):
    return text.replace("\\", "\\\\").replace("]", "\\]")


def writeInitialStones(file, string):
    for i in range(0, len(string), 2):
        file.write("[")
        file.write(string[i : i + 2])
        file.write("]")


def otherPlayer(player):
    return "B" if player == "W" else "W"


def writeCoordinates(file, node):
    file.write(chr(97 + node["x"]))
    file.write(chr(97 + node["y"]))


def writeCoordinatesInBrackets(file, node):
    file.write("[")
    writeCoordinates(file, node)
    file.write("]")


def writeMarks(file, marks):
    for mark in marks:
        if "letter" in mark["marks"]:
            file.write("LB[")
            writeCoordinates(file, mark)
            file.write(":")
            file.write(escape(mark["marks"]["letter"]))
            file.write("]")
        elif "triangle" in mark["marks"]:
            file.write("TR")
            writeCoordinatesInBrackets(file, mark)
        elif "square" in mark["marks"]:
            file.write("SQ")
            writeCoordinatesInBrackets(file, mark)
        elif "cross" in mark["marks"]:
            file.write("MA")
            writeCoordinatesInBrackets(file, mark)
        elif "circle" in mark["marks"]:
            file.write("CR")
            writeCoordinatesInBrackets(file, mark)


def prependText(node, text):
    if "text" in node:
        node["text"] = text + "\n\n" + node["text"]
    else:
        node["text"] = text


def writeNode(file, node, player):
    if "marks" in node:
        writeMarks(file, node["marks"])
    if "correct_answer" in node:
        prependText(node, "CORRECT")
    elif "wrong_answer" in node:
        prependText(node, "WRONG")
    if "text" in node:
        file.write("C[")
        file.write(escape(node["text"]))
        file.write("]")
    if "branches" in node:
        branches = node["branches"]
        for branch in branches:
            if len(branches) > 1:
                file.write("(")
            writeBranch(file, branch, player)
            if len(branches) > 1:
                file.write(")")


def writeBranch(file, branch, player):
    file.write(";")
    file.write(player)
    writeCoordinatesInBrackets(file, branch)
    writeNode(file, branch, otherPlayer(player))


def writePuzzle(file, puzzle):
    file.write("(;FF[4]CA[UTF-8]AP[puzzle2sgf:0.1]GM[1]GN[")
    file.write(escape(puzzle["name"]))
    file.write("]SZ[")
    file.write(str(puzzle["width"]))
    if puzzle["width"] != puzzle["height"]:
        file.write(":")
        file.write(str(puzzle["height"]))
    file.write("]")
    initial_black = puzzle["initial_state"]["black"]
    if initial_black:
        file.write("AB")
        writeInitialStones(file, initial_black)
    initial_white = puzzle["initial_state"]["white"]
    if initial_white:
        file.write("AW")
        writeInitialStones(file, initial_white)
    prependText(puzzle["move_tree"], puzzle["puzzle_description"])
    player = puzzle["initial_player"][0].upper()
    file.write("PL[")
    file.write(player)
    file.write("]")
    writeNode(file, puzzle["move_tree"], player)
    file.write(")")


def authenticate():
    url = "https://online-go.com/api/v0/login"
    username = input("Username: ")
    password = input("Password: ")
    response = requests.post(url, data={"username": username, "password": password})
    return response.cookies


cookies = [] if skipAuthentication else authenticate()
if downloadWholeCollection:
    collectionUrl = (
        "https://online-go.com/api/v1/puzzles/"
        + str(puzzleNumber)
        + "/collection_summary"
    )
    collection = requests.get(collectionUrl, cookies=cookies).json()
    time.sleep(5.0)
puzzleUrl = "https://online-go.com/api/v1/puzzles/" + str(puzzleNumber)
responseJSON = requests.get(puzzleUrl, cookies=cookies).json()
if downloadWholeCollection:
    # collectionName = responseJSON["collection"]["name"]
    collectionName = (
        re.sub(r"[^A-Za-z0-9_-]+", "_", responseJSON["collection"]["name"])
        + "_"
        + puzzle_n
    )

    collectionFolder = os.getcwd() + "/" + collectionName
    os.mkdir(collectionFolder)
    os.chdir(collectionFolder)

cleansed_puzzle_name = (
    re.sub(r"[^A-Za-z0-9_-]+", "_", responseJSON["name"]) + "_" + puzzle_n
)
with open(cleansed_puzzle_name + ".sgf", "w", encoding="utf-8") as file:
    writePuzzle(file, responseJSON["puzzle"])
if downloadWholeCollection:
    for puzzle in collection:
        if puzzle["id"] != puzzleNumber:
            time.sleep(5.0)
            puzzleUrl = "https://online-go.com/api/v1/puzzles/" + str(puzzle["id"])
            puzzleJSON = requests.get(puzzleUrl, cookies=cookies).json()["puzzle"]
            cleansed = (
                re.sub(r"[^A-Za-z0-9_-]+", "_", puzzle["name"])
                + "_"
                + str(puzzle["id"])
            )
            with open(cleansed + ".sgf", "w", encoding="utf-8") as file:
                writePuzzle(file, puzzleJSON)
