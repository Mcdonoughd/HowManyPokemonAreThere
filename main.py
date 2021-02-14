# Calculate how many Unique Pokemon there are

import json
import numpy.polynomial.polynomial as poly
import math
import sys
import numpy as np

np.set_printoptions(threshold=sys.maxsize)
np.set_printoptions(precision = 30, suppress = True)
# Permute
def P(n, r,repeat):
    if repeat:
        return math.pow(n, r)
    else:
        if r > n:
            return 0
        num = math.factorial(n)
        denom = math.factorial(n - r)
        return num / denom

# Choose
def C(n, r,repeat):
    if r>n:
        return 0
    if repeat:
        num = math.factorial(n+r-1)
        denom = math.factorial(r) * math.factorial(n - r)
        return num / denom
    else:
        num = math.factorial(n)
        denom = math.factorial(r) * math.factorial(n - r)
        return num / denom

def starsbars(totalLimit,boxLimit,boxNum):
    # Init a list of coeffs
    polyCoeff = [0]*(boxLimit+1)
    polyCoeff[boxLimit] = -1
    polyCoeff[0] = 1
    # Poly Coeff should be 1-x^boxLimit

    # Expand the polynomial to be (1-x^boxLimit)^boxNum
    expandedPolyCoeff = poly.polypow(polyCoeff,boxNum)

    # Get terms that are valid
    validPolyCoeff = expandedPolyCoeff[:totalLimit]

    # Get teh powers of the valid terms
    powers = [i for i,v in enumerate(validPolyCoeff) if (v)]
    # Get the coeffs of the valid terms
    coeffs = [v for i,v in enumerate(validPolyCoeff) if (v)]

    # substituting the generative function
    finalpowers = [(i * -1)+totalLimit for i in powers]
    # print(finalpowers)


    # Better explanation: https://math.stackexchange.com/questions/1922819/stars-and-bars-with-bounds
    # Here we have limit = 127, cap = 63, entities = 6
    # [x^limit](1-x^cap)^entities * sum(k+entities-1/entities-1)x^k
    # expressing the above you get the following
    # [x^limit]x^{384}-6x^{320}+15x^{256}-20x^{192}+15x^{128}-6x^{64}+1 * sum(k+entities-1/entities-1)x^k
    # we can then apply [x^{p-q}]A(x)=[x^p]x^{q}A(x)
    # [x^{-257}]-6[x^{-193}]+15[x^{-129}]-20[x^{-65}]+15[x^{-1}]-6x^{63}+[x^127] * sum(k+entities-1/entities-1)x^k
    # because negative exponents dont do anything we can simplify to
    # -6[x^{63}]+[x^127] * sum(k+entities-1/entities-1)x^k
    #  which simplifies to -6(68 nCr 5)+(132 nCr 5)
    # 241888308

    # For this case we need to
    # sum all posibilites from 0 to limit
    finalAnswer = 0
    for idx,value in enumerate(finalpowers):
        finalAnswer+= coeffs[idx]*C(finalpowers[idx]+boxNum-1, boxNum-1,False)
    if finalAnswer == 0:
        # This is just to count the posibility of no EVs
        finalAnswer+=1
    # print(finalAnswer)
    return finalAnswer

def getEvPossibilities():
    totalLimit = 127
    boxLimit = 63
    boxNum = 6

    totalPossibilities = 0
    for totalEvs in range(totalLimit+1):
        totalPossibilities += starsbars(totalEvs, boxLimit, boxNum)

    return totalPossibilities


# return number of combination of moves a pokemon can learn
# A pokemon can learn upto 4 moves at a time, so we must also take into the posibility that a pokemon has only 3 moves
def numMovesCominations(numMoves):
    moveCombos = 0
    for i in range(1,4):
        moveCombos += C(numMoves, i,False)
    return moveCombos


# 6 IVs that range from 0-31 (equivalent to 32 pick 1, 6 times)
def numIVCombinations():
    return P(32,6,True)

def get_keys(dl, keys_list):
    if isinstance(dl, dict):
        keys_list += dl.keys()
        map(lambda x: get_keys(x, keys_list), dl.values())
    elif isinstance(dl, list):
        map(lambda x: get_keys(x, keys_list), dl)

def main():
    # Get our constant terms
    IVs = numIVCombinations()
    EVs = getEvPossibilities()
    Natures = 25
    Shiny = 2

    # # I played around with also adding held items
    # with open('item.json', 'r') as myfile:
    #     data = myfile.read()
    # obj = json.loads(data)
    # numItems = obj['count']
    # itemList = obj['results']

    # print("Num Held Items: " + str(numItems))

    # Load learnsets
    with open('Learnsets.json', 'r') as myfile:
        data = myfile.read()
    learnsets = json.loads(data)

    learnsets_keys = []
    get_keys(learnsets, learnsets_keys)

    # Load Pokemon
    with open('Pokedex.json', 'r') as myfile:
        data = myfile.read()
    obj = json.loads(data)

    keys = []
    get_keys(obj, keys)

    # Do the main calculation
    numpokemon = 0
    moveset = []
    totalPossibilities = 0
    for i in keys:
        # Stop at the first instance of nonPokemon
        if i == "missingno":
            break

        print(i + ":")
        numpokemon += 1
        print("EV Combinations: " + str(EVs))
        print("IV Combinations: " + str(IVs))
        print("Num Natures: " + str(25))

        # Get number of abilities
        abilities = []
        get_keys(obj[i]['abilities'], abilities)
        Abilities = len(abilities)
        print("Num Abilities: " + str(Abilities))

        # Get moveset posibilities
        try:
            tmpmoveset = []
            get_keys(learnsets[i]["learnset"], tmpmoveset)
            moveset = tmpmoveset
        except:
            print("Moveset exception: probably a mega or a some other form, using previous moveset")

        # print(moveset)
        print("Num Moves: " + str(len(moveset)))
        Moves = numMovesCominations(len(moveset))
        print("Num Moves Combination: " + str(Moves))

        # Get genders
        Gender = 1
        try:
            t = obj[i]['genderRatio']

            # print("Genders: " + str(len(t.keys())))
            Gender = 2
            #     if this exists then the pokemon has 2 genders
        except:
            # print(i + " has no genderRatio field")
            try:
                # if the gender key exists then the pokemon only has 1 static gender
                t = obj[i]['gender']
                Gender = 1
            except:
                # otherwise there are 2 genders at standard genderRatio
                Gender = 2
        print("Genders: " + str(Gender))


        # Put it all together
        posibilities = IVs * EVs * Natures * Moves * Abilities * Shiny * Gender

        print(i + " Combinations: " + str(posibilities))
        print()

        totalPossibilities += posibilities

    print("Total Pokemon Count: " + str(numpokemon))
    print("Total Possibilities: " + str(int(totalPossibilities)))



if __name__ == '__main__':
    main()

