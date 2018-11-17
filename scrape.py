import csv

import unidecode
import requests
from bs4 import BeautifulSoup


URL = 'https://nathansfamous.com/promos-and-fanfare/hot-dog-eating-contest/hall-of-fame/'

# grab the HTML and turn it into soup
r = requests.get(URL)
soup = BeautifulSoup(r.text, 'html.parser')

# grab a list of h3 nodes, which have the years of each contest
years = soup.find_all('h3')


def get_winners(year_node):
    '''given a year node, grab the winner data and return
       a list of lists formatted to correspond to these headers:
           ['year', 'name', 'hotdogs', 'gender']
       🌭 emojis represents missing values
    '''

    # get actual text of year
    year = year_node.text.strip()
    
    # skip the records before 2002, which only include actual winner
    if '2001' in year:
        return

    # a list to hold all the data
    ls = []

    # let's find the container, shall we
    winner_panel = None
    
    # iterate over h3 node parents
    for parent in year_node.parents:

        # does it have a class attribute?
        classlist = parent.attrs.get('class')

        # if so, and 'winner-panel' is in there,
        # this is our horse
        if classlist and 'winner-panel' in classlist:
            # set the one thing equal to the other thing
            winner_panel = parent

            # and stop
            break

    # grab a handle to the div(s) with the actual winners 
    winners = winner_panel.find_all('div', {'class': 'winner'})


    def get_winner_deets(div, gender='🌭'):
        '''given a div with the winner info, return a list
           with the information we seek
           ... for contests that don't specify gender, we assume
           a gender of 🌭
        '''

        # grab the name
        winner_name = div.find('p', {'class': 'name'}).text.strip()

        # kill garbage chars
        winner_name_clean = unidecode.unidecode(winner_name)

        # grab the number of hot dogs eaten and turn it into
        # a float
        hd_eaten = float(div.find('p', {'class': 'number-of-hot-dogs-eaten'}).text.split()[0])
        
        # return a list of that hot mustardy data yeahhhhh
        return [year, winner_name_clean, hd_eaten, gender]


    # if this is a gendered contest, there will be two winner divs
    if len(winners) > 1:

        # grab a handle to each one
        winner_m, winner_f = winners

        # call function to get winner deets from the dude
        dude = get_winner_deets(winner_m, 'm')

        # and append that list to the big list
        ls.append(dude)

        # same for nondudes
        dudette = get_winner_deets(winner_f, 'f')
        ls.append(dudette)

    # pre-2011 contests were co-ed, so there's just one item in
    # our list of winner divs
    else:
        # grab deets and append
        winner = get_winner_deets(winners[0])
        ls.append(winner)

    # next, grab the unordered lists with the runnerup data
    runnersup = winner_panel.parent.find_all('ul')


    def get_runnerup_deets(ul, gender='🌭'):
        '''given a `ul` list of runnersup, parse out the data and
           return a list of lists of that data
           ... for contests that don't specify gender, we assume
           a gender of 🌭
        '''

        # grab the list items
        ru = ul.find_all('li')

        # an interim list to hold the data as we iterate
        ru_ls = []

        # loop over the items in the list
        for human in ru:

            # try to grab the number of hot dogs eaten as a float
            # got a corner case without a total, which throws everything off
            # so for that one we have a record of 🌭 hot dogs eaten
            try:
                hotdogs = float(human.text.rsplit(' ', 1)[-1])
                # grab the name out of there
                name = human.text.rsplit(' ', 1)[0].replace(':', '').strip()
            except ValueError:
                hotdogs = '🌭'
                name = human.text.replace(':', '').strip()

            # kill garbage chars
            name_clean = unidecode.unidecode(name)

            # append to our interim list
            ru_ls.append([year, name_clean, hotdogs, gender])
        
        # return the interim list
        return ru_ls

    # if this is a gendered contest
    if len(runnersup) > 1:

        # grab a handle to each list
        runnersup_m, runnersup_f = runnersup
        
        # get deets on dude runnersup
        ru_dudes = get_runnerup_deets(runnersup_m, gender='m')

        # loop over that list and append each one to the master list
        # dang we are doing a lot of passing data between lists here but that's ok
        for ru in ru_dudes:
            ls.append(ru)

        # same for nondudes
        ru_dudettes = get_runnerup_deets(runnersup_f, gender='f')
        
        for ru in ru_dudettes:
            ls.append(ru)
    
    # if it's not a gendered contest, there's only one
    # item in the list of `ul` nodes
    else:
        # grab deets for those peeps here
        runnersup_ls = get_runnerup_deets(runnersup[0])

        # loop over and append
        for ru in runnersup_ls:
            ls.append(ru)

    # return that big old list of data
    return ls


# open a file
with open('hotdog-contest.csv', 'w', newline='', encoding='utf-8') as outfile:

    # create a writer object, single-quote character because some people
    # have nicknames, e.g. Pat "Deep Dish" Bertoletti
    # and quote all nonnumeric fields
    writer = csv.writer(outfile)

    # write header row
    writer.writerow(['year', 'name', 'hotdogs', 'gender'])

    # loop over the year nodes we grabbed way up above there
    for year in years:

        # call that big ol' function on it
        winner_data = get_winners(year)

        # if it returns something, write rows to file
        if winner_data:
            writer.writerows(winner_data)
