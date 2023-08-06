import pickle


from nagfactoryTests import nagfromtestdata

expectedresultsfolder = 'ExpectedResults'


def buildexpectedresults(nag):
    with open(expectedresultsfolder + '/nag_attributes.pickle', 'w') as f:
        pickle.dump(nag.attributes, f)


if __name__ == '__main__':
    #Fully hydrated nag object with test data
    buildexpectedresults(nagfromtestdata())
    print 'done'
