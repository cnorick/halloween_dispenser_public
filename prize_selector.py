from enum import IntEnum
import pprint
import random

# For calculating random distribution
NUM_SM = 600
NUM_MD = 350
NUM_FULL_SIZE = 98
TOTAL_CANDY = NUM_SM + NUM_MD + NUM_FULL_SIZE
NUM_PRIZES = 450 # Number of expected trick-or-treaters + repeats
REDISTRIBUTION_RATE = 0.001
MIN_CHANCE = 0.05 # Minimum chance of any given medium prize (not single and not full-size)

SM_PER_SPIN = 1.23 # Experimentally found how many get dropped on average
MD_PER_SPIN = 1

class Prize(IntEnum):
   singleSm = 0,
   singleMd = 1,
   doubleSm = 2,
   doubleMd = 3,
   singleSmAndSingleMd = 4,
   doubleSmAndSingleMd = 5,
   quadrupleSm = 6,
   singleFullsized = 7,


class PrizeSelector:
    def __init__(self):
        self._setDistributions()
        totalDistribution = sum(self.distributions.values())
        pprint.pprint(self.distributions)
        print(totalDistribution)
        print("expected Sm: " + str(self._getExpectedTotalSm(self.distributions)))
        print("expected Md: " + str(self._getExpectedTotalMd(self.distributions)))
        print("expected Full Sized: " + str(self.distributions[Prize.singleFullsized] * NUM_PRIZES))
        print("chance of small prize: " + str(self.distributions[Prize.singleSm] + self.distributions[Prize.singleMd]))
        print("chance of medium prize: " + str(self.distributions[Prize.doubleSm] + self.distributions[Prize.doubleMd] + self.distributions[Prize.singleSmAndSingleMd] + self.distributions[Prize.doubleSmAndSingleMd]))
        print("chance of large prize: " + str(self.distributions[Prize.quadrupleSm] + self.distributions[Prize.singleFullsized]))

    def getRandomPrize(self):
        randomNum = random.random()
        runningTotal = 0
        for prize, dist in self.distributions.items():
            runningTotal += dist
            if (randomNum <= runningTotal):
                return prize

    def _setDistributions(self):
        # We know how many full sized bars we have, so we can figure out how often to give out full sized bars
        fullSizeDist = NUM_FULL_SIZE / NUM_PRIZES
        remainingDistribution = 1 - fullSizeDist

        # Start by giving out as many big prizes as possible.
        # Then if we don't have enough candy based on those distributions, we'll iteratively
        # lower the chances of getting multiples and increase the chances of getting singles
        # I couldn't come up with a way to calculate distributions given the known quantities, so this
        # is just a trail and error algorithm that runs until the distributions are such that we
        # have enough candy.
        self.distributions = {
            Prize.singleSm: 0,
            Prize.singleMd: 0,
            Prize.doubleSm: remainingDistribution / 5,
            Prize.doubleMd: remainingDistribution / 5,
            Prize.singleSmAndSingleMd: remainingDistribution / 5,
            Prize.doubleSmAndSingleMd: remainingDistribution / 5,
            Prize.quadrupleSm: remainingDistribution / 5,
            Prize.singleFullsized: fullSizeDist
        }

        while not self._isValidDistribution(self.distributions):
            if(not self._isValidSmDistribution(self.distributions)):
                self._redistributeSm()
            if(not self._isValidMdDistribution(self.distributions)):
                self._redistributeMd()

    def _isValidDistribution(self, dist):
        return self._isValidSmDistribution(dist) and self._isValidMdDistribution(dist)

    # Makes sure that we won't give out more candy than we have
    def _isValidSmDistribution(self, dist):
        return self._getExpectedTotalSm(dist) <= NUM_SM

    def _isValidMdDistribution(self, dist):
        return self._getExpectedTotalMd(dist) <= NUM_MD

    # Given the distributions and the number of kids, return the expected number of bars to be given out
    def _getExpectedTotalSm(self, dist):
        return SM_PER_SPIN * (
            dist[Prize.singleSm] * NUM_PRIZES * 1 + \
            dist[Prize.doubleSm] * NUM_PRIZES * 2 + \
            dist[Prize.quadrupleSm] * NUM_PRIZES * 4 + \
            dist[Prize.singleSmAndSingleMd] * NUM_PRIZES * 1 + \
            dist[Prize.doubleSmAndSingleMd] * NUM_PRIZES * 2
        )

    # Given the distributions and the number of kids, return the expected number of bags to be given out
    def _getExpectedTotalMd(self, dist):
        return MD_PER_SPIN * (
            dist[Prize.singleMd] * NUM_PRIZES * 1 + \
            dist[Prize.doubleMd] * NUM_PRIZES * 2 + \
            dist[Prize.singleSmAndSingleMd] * NUM_PRIZES * 1 + \
            dist[Prize.doubleSmAndSingleMd] * NUM_PRIZES * 1
        )

    # Removes from multi bar prizes and add to the single
    def _redistributeSm(self):
        canDistribute = False
        newRate = REDISTRIBUTION_RATE / 3 # Since there are 3 different multi bar prizes

        if (self.distributions[Prize.doubleSm] - newRate > MIN_CHANCE):
            canDistribute = True
            self.distributions[Prize.doubleSm] -= newRate
            self.distributions[Prize.singleSm] += newRate

        if (self.distributions[Prize.quadrupleSm] - newRate > MIN_CHANCE):
            canDistribute = True
            self.distributions[Prize.quadrupleSm] -= newRate
            self.distributions[Prize.singleSm] += newRate

        if (self.distributions[Prize.doubleSmAndSingleMd] - newRate > MIN_CHANCE):
            canDistribute = True
            self.distributions[Prize.doubleSmAndSingleMd] -= newRate
            self.distributions[Prize.singleSm] += newRate / 2
            # Since doubleBarAndSingleBag also contains a bag, we have to add part back to the the single bag
            self.distributions[Prize.singleMd] += newRate / 2

        if (not canDistribute):
            raise Exception("Could not redistribute small sized candy. Buy more candy")

    def _redistributeMd(self):
        if (self.distributions[Prize.doubleMd] - REDISTRIBUTION_RATE > MIN_CHANCE):
            self.distributions[Prize.singleMd] += REDISTRIBUTION_RATE
            self.distributions[Prize.doubleMd] -= REDISTRIBUTION_RATE
        else:
            raise Exception("Could not redistribute medium sized candy. Buy more candy")

