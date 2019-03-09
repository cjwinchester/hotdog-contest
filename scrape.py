import csv

import requests
from bs4 import BeautifulSoup


CSV_FILE = 'hotdog-contest.csv'
URL = 'https://nathansfamous.com/hot-dog-eating-contest/hall-of-fame/'

# fetch the page
r = requests.get(URL)

# fix some garbage chars
fixes = (
    ('â', "'"),
    ('â', '"'),
    ('â', '"')
)

fixed_text = r.text

for x in fixes:
    fixed_text = fixed_text.replace(*x)

# turn the HTML into soup
soup = BeautifulSoup(fixed_text, 'html.parser')

# find the contests
contests = soup.select('.result-panel')

# skip <=2001 records, which only list the winner
target_contests = [x for x in contests
                   if '2001' not in x.find('h3').text]

with open(CSV_FILE, 'w') as outfile:

    # define headers
    headers = ['year', 'name', 'hotdogs_eaten', 'gender']

    # set up the file to write to
    writer = csv.DictWriter(outfile, fieldnames=headers)

    # write out headers
    writer.writeheader()

    # loop over each contest
    for div in target_contests:

        # find the year
        year = int(div.find('h3').text)

        # find the winners
        winners = div.select('div.winner')

        # set up a dict for genders
        # for gendered contests, the first instance of each winner
        # (and list of runners-up) is men, second is women
        gender_dict = {
            0: 'm',
            1: 'f'
        }

        # loop over the winner divs
        for i, winner in enumerate(winners):

            # if there is more than one winner, it's a gendered contest
            if len(winners) > 1:
                # ... so set the value accordingly
                gender = gender_dict[i]
            else:
                # otherwise, leave blank
                gender = ''

            # find the winner's name
            winner_name = winner.find('p', {'class': 'name'}).text

            # find the number of hot dogs eaten and
            # kill the words
            winner_count = float(winner.find('p', {'class': 'number-of-hot-dogs-eaten'}).text.replace(' Hot Dogs', '')) # NOQA

            winner_data = [year, winner_name, winner_count, gender]

            # write out the row of data
            writer.writerow(dict(zip(headers, winner_data)))

        # find the list(s) of runnersup
        runners_up_list = div.find_all('ul')

        # loop over the runners-up lists
        for i, rlist in enumerate(runners_up_list):

            # if more than one list, it's a gendered contest
            if len(runners_up_list) > 1:
                # ... so set the value accordingly
                gender = gender_dict[i]
            else:
                # otherwise, leave blank
                gender = ''

            # get the people in this list
            runnersup = rlist.find_all('li')

            # loop over the people
            for human in runnersup:

                # grab the number of hot dogs eaten
                hotdogs = human.text.rsplit(' ', 1)[-1]

                # Meredith Boxberger did not have a total listed
                # for her 2016 finish, so deal with that here
                # per an email from the sanctioning body,
                # she ate 15.5 that year
                if hotdogs == 'Boxberger' and year == 2016:
                    name = 'Meredith Boxberger'
                    hotdogs = 15.5
                else:
                    # grab the name out of there
                    name = human.text.rsplit(' ', 1)[0] \
                                .replace(':', '').strip()

                    # and turn the hot dog count into a float
                    hotdogs = float(hotdogs)

                # dump the data into a list
                data = [year, name, hotdogs, gender]

                # and write out to file
                writer.writerow(dict(zip(headers, data)))
