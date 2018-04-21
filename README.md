# RedditLoves

Wanted to figure out which country people posted the most about in a specific subreddit.
Because I swear there are large number of upvoted Reddit posts with the country "Japan" in the title.

## How to use
python3 redditr.py [subreddit] [top/controversial/hot/new] [number of results to display]

### Example
python3 redditr.py pics top 10

## Data
List of countries/nationalities/alpha codes acquired from https://github.com/Dinu/country-nationality-list/blob/master/countries.json

List of cities/provinces acquired from basic version of https://simplemaps.com/data/world-cities

I preprocessed through the two data sources to ensure the country names could be joined on.

Also added in an extra_countries.json for countries such as Scotland, Wales, because these are mentioned often on Reddit.

Korea is added, to amalgamate results from both North and South, as well as to include post titles which use abbreviations such as N.Korea or S.Korea.

Great Britain, Britain, England all seemed to be interchangeable, so I added in Britain and England to extra_countries.json and amalgamated all the results together for the final result.

## How this works
* Looks through 1000 posts in the specified subreddit and section
* Cities are populated under the country key in the dictionary
* Loops through each country and checks if the country, alpha codes or nationality is mentioned in the title.
* Then loops through each city or province in the country to check if the city/province was mentioned in the title.
* If a match is found for any of the above, we increment the number of mentions of a country by 1.

* The checks are done via regex matching, "(^|\s)city($|\s)", the city/province must either appear at the beginning or end of the title, or
in the middle of the title. This ensures we don't match false positives such as "Ichina" -> China.

* I also maintain the population count of each city, and assume the topic of the post is aimed at the more popular city.
* This mitigates false positives such as Melbourne in USA vs Melbourne in Australia. Obviously there could still be a slight chance the
post would be about USA.

## Problems/False positives
* As discussed previously, the only method is distinguishing the same city names in different countries is by population count which is a rudimentary technique.
* Provinces such as "Central" in Ghana may be detected when the post title is completely irrelevant, such as "Central Park, NYC"
* On the topic of NYC, city abbreviations are not checked, because I felt it was slightly overkill for what I just wanted to achieve, I solely wanted rough estimates of which countries Reddit mentioned the most.
* Ivory Coast has a city named Man which produced false positives for posts such as "Man comes back from war"


